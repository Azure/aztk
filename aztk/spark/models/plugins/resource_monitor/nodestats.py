"""TVM stats"""

# stdlib imports
import logging
from datetime import datetime
import os
import time
import platform
from collections import namedtuple
import sys


# non-stdlib imports
import psutil
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

VERSION = "0.0.1.1"
_DEFAULT_STATS_UPDATE_INTERVAL = 5

HOST = '127.0.0.1'
PORT = 8086
USER = 'admin'
PASSWORD = 'password'
DBNAME = 'data'

def setup_logger():
    # logger defines
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03dZ %(levelname)s %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = setup_logger()


# global defines
_IS_PLATFORM_WINDOWS = platform.system() == 'Windows'


def python_environment():  # pragma: no cover
    """
    Returns the current python environment information
    """
    return ' '.join([platform.python_implementation(), platform.python_version()])


def os_environment():
    """
    Get the OS environment
    """
    return platform.platform()

def avg(list):
    """
        Compute the average of a list
    """
    return sum(list) / float(len(list))


def pretty_nb(num, suffix=''):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1000.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


NodeIOStats = namedtuple('NodeIOStats', ['read_bps', 'write_bps'])


class NodeStats:
    """Persistent Task Stats class"""

    def __init__(self,
                 num_connected_users=0,
                 num_pids=0,
                 cpu_count=0,
                 cpu_percent=None,
                 mem_total=0,
                 mem_avail=0,
                 swap_total=0,
                 swap_avail=0,
                 disk_total=0,
                 disk=None,
                 net=None):
        """
        Map the attributes
        """
        self.num_connected_users = num_connected_users
        self.num_pids = num_pids
        self.cpu_count = cpu_count
        self.cpu_percent = cpu_percent
        self.mem_total = mem_total
        self.mem_avail = mem_avail
        self.swap_total = swap_total
        self.swap_avail = swap_avail
        self.disk_total = disk_total
        self.disk = disk or NodeIOStats()
        self.net = net or NodeIOStats()

    @property
    def mem_used(self):
        """
            Return the memory used
        """
        return self.mem_total - self.mem_avail


class IOThroughputAggregator:
    def __init__(self):
        self.last_timestamp = None
        self.last_read = 0
        self.last_write = 0

    def aggregate(self, cur_read, cur_write):
        """
            Aggregate with the new values
        """
        now = datetime.now()
        read_bps = 0
        write_bps = 0
        if self.last_timestamp:
            delta = (now - self.last_timestamp).total_seconds()
            read_bps = (cur_read - self.last_read) / delta
            write_bps = (cur_write - self.last_write) / delta

        self.last_timestamp = now
        self.last_read = cur_read
        self.last_write = cur_write

        return NodeIOStats(read_bps, write_bps)


class NodeStatsCollector:
    """
    Node Stats Manager class
    """

    def __init__(self, pool_id, node_id, refresh_interval=_DEFAULT_STATS_UPDATE_INTERVAL):
        self.pool_id = pool_id
        self.node_id = node_id
        self.telemetry_client = None
        self.first_collect = True
        self.refresh_interval = refresh_interval

        self.disk = IOThroughputAggregator()
        self.network = IOThroughputAggregator()
        self.telemetry_client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DBNAME)

    def init(self):
        """
            Initialize the monitoring
        """
        # start cpu utilization monitoring, first value is ignored
        psutil.cpu_percent(interval=None, percpu=True)

    def _get_network_usage(self):
        netio = psutil.net_io_counters()
        return self.network.aggregate(netio.bytes_recv, netio.bytes_sent)

    def _get_disk_usage(self):
        diskio = psutil.disk_io_counters()
        return self.disk.aggregate(diskio.read_bytes, diskio.write_bytes)

    def _sample_stats(self):
        # get system-wide counters
        mem = psutil.virtual_memory()
        disk_stats = self._get_disk_usage()
        net_stats = self._get_network_usage()

        swap_total, _, swap_avail, _, _, _ = psutil.swap_memory()

        stats = NodeStats(
            cpu_count=psutil.cpu_count(),
            cpu_percent=psutil.cpu_percent(interval=None, percpu=True),
            num_pids=len(psutil.pids()),

            # Memory
            mem_total=mem.total,
            mem_avail=mem.available,
            swap_total=swap_total,
            swap_avail=swap_avail,

            # Disk IO
            disk=disk_stats,

            # Net transfer
            net=net_stats,
        )
        del mem
        return stats

    def _collect_stats(self):
        """
            Collect the stats and then send to app insights
        """
        # collect stats
        stats = self._sample_stats()

        if self.first_collect:
            self.first_collect = False
            return

        if stats is None:
            logger.error("Could not sample node stats")
            return

        if self.telemetry_client:
            self._send_stats(stats)
        else:
            self._log_stats(stats)

    def _send_stats(self, stats):
        """
            Retrieve the current stats and send to app insights
        """
        process = psutil.Process(os.getpid())

        logger.debug("Uploading stats. Mem of this script: %d vs total: %d",
                     process.memory_info().rss, stats.mem_avail)
        now = datetime.utcnow()
        series = []

        # TODO: Add an item to properties to express the role of the node
        # TODO: in the cluster. For example:
        # TODO: properties={"role": "master"}
        # TODO: properties={"role": "server"}

        for cpu_n in range(0, stats.cpu_count):
            # client.track_metric("Cpu usage",
            #                     stats.cpu_percent[cpu_n], properties={"Cpu #": cpu_n})
            series.append(self._fill_template(now,
                "Cpu usage",
                stats.cpu_percent[cpu_n],
                properties={"Cpu #": cpu_n}))

        series.append(self._fill_template(now, "Memory used", stats.mem_used))
        series.append(self._fill_template(now, "Memory available", stats.mem_avail))
        series.append(self._fill_template(now, "Disk read", stats.disk.read_bps))
        series.append(self._fill_template(now, "Disk write", stats.disk.write_bps))
        series.append(self._fill_template(now, "Network read", stats.net.read_bps))
        series.append(self._fill_template(now, "Network write", stats.net.write_bps))

        # print("Write points to database: {0}".format(series))
        self.telemetry_client.write_points(series)#, retention_policy=retention_policy)

    def _fill_template(self, date, metric, value, properties = None):
        hostName = self.node_id
        template = {
            "time": date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "measurement": metric,
            "fields": {
                "value": value,
            },
            "tags": {
                "hostName": hostName,
            },
        }

        if properties is not None:
            template['tags'] = {**template['tags'], **properties}

        return template

    def _log_stats(self, stats):
        logger.info("========================= Stats =========================")
        logger.info("Cpu percent:            %d%% %s",
                    avg(stats.cpu_percent), stats.cpu_percent)
        logger.info("Memory used:       %sB / %sB",
                    pretty_nb(stats.mem_used), pretty_nb(stats.mem_total))
        logger.info("Swap used:         %sB / %sB",
                    pretty_nb(stats.swap_avail), pretty_nb(stats.swap_total))
        logger.info("Net read:               %sBs",
                    pretty_nb(stats.net.read_bps))
        logger.info("Net write:              %sBs",
                    pretty_nb(stats.net.write_bps))
        logger.info("Disk read:               %sBs",
                    pretty_nb(stats.disk.read_bps))
        logger.info("Disk write:              %sBs",
                    pretty_nb(stats.disk.write_bps))
        logger.info("-------------------------------------")
        logger.info("")

    def run(self):
        """
            Start collecting information of the system.
        """
        print('try to create database {}'.format(DBNAME))

        logger.debug("Start collecting stats for pool=%s node=%s",
                     self.pool_id, self.node_id)

        while True:
            self._collect_stats()
            time.sleep(self.refresh_interval)


def main():
    """
    Main entry point for prism
    """
    # log basic info
    logger.info("Python args: %s", sys.argv)
    logger.info("Python interpreter: %s", python_environment())
    logger.info("Operating system: %s", os_environment())
    logger.info("Cpu count: %s", psutil.cpu_count())

    pool_id = os.environ.get('AZ_BATCH_POOL_ID', '_test-pool-1')
    node_id = os.environ.get('AZ_BATCH_NODE_ID', '_test-node-1')

    if len(sys.argv) > 0:
        HOST = sys.argv[1]

    logger.info('setting host to {}'.format(HOST))

    # get and set event loop mode
    logger.info('enabling event loop debug mode')
    logger.info('cluster_id {}'.format(pool_id))
    logger.info('node_id    {}'.format(node_id))


    # create node stats manager
    collector = NodeStatsCollector(pool_id, node_id)
    collector.init()
    collector.run()


if __name__ == '__main__':
    main()
