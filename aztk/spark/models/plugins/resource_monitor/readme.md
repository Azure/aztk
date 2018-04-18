# Using the Resrouce Monitor Plugin

The resource monitor plugin is useful for tracking performance counters on the cluster. These include counters such as Percent CPU used per core, Disk Read, Disk Write, Network In, Network out, and several others. Simply enabling the plugin in your cluster.yaml will deploy all the necessary components to start tracking metrics.

## Setup

Update your cluster.yaml file to include the plugin as follows:

```yaml
...

plugins:
  - name: resource_monitor

...


```

Once the cluster is created simply the cluster ssh command and all of the ports will automatically get forwareded.

```sh
aztk spark cluster ssh --id <my_cluster>
```

### Configuration and passwords
The default environement is configured in the .env file for the plugin. We highly recommend updating the user names and passwords before deploying your cluster.

```sh
# Example .env file please modify and DO NOT USE AS IS
INFLUXDB_USER=admin
INFLUXDB_USER_PASSWORD=password
INFLUXDB_ADMIN_ENABLED=true
INFLUXDB_DATA_LOCATION=/mnt/batch/tasks/shared/influxdb
GF_SECURITY_ADMIN_PASSWORD=password
GRAFANA_DATA_LOCATION=/mnt/batch/tasks/shared/grafana

```

### Ports
url | desciption
--- | ---
http://localhost:8083 | InfluxDB Query UI
http://localhost:8086 | InfluxDB API endpoint
http://localhost:3000 | Grafana UI

## Querying the database
This plugin uses an on-disk [InfluxDB database](https://www.influxdata.com/) on the master node to track all of the metrics. The database is available while the cluster is up and running and destroyed when the cluster is deleted.

After running the **cluster ssh** command simply navigate to http://loclahost:8083.

![InfluxDB query UI](./images/influx_query.png)

All of the performance counter metrics are stored in a database called **data**. In the top right corner of the web page, change the default database to use **data**.

## Data
The metrics currently pushed are listed below.

Measurement | Description
--- | ---
Cpu usage | Percentage of cpu used per core
Disk read | Bytes read
Disk write | Bytes written
Memory available | Bytes available
Memory used | Bytes used
Network read | Bytes read
Network write | Byres written

To view the what measurements are available you can simply run the show measurements command in the query bar.
```sql
/* Show all measurements */
SHOW MEASUREMENTS

/* Show keys for a specific measurements */
SHOW TAG KEYS FROM "Cpu usage"

/* Show all distict values for a specific tag of a measurement */
SHOW TAG VALUES FROM "Cpu usage" WITH KEY = "Cpu #"
```

## Visualize data in Grafana
[Grafana](https://grafana.com/) is a nice visualization tool that can pull data from InfluxDB. The UI is available while the cluster is up and running and destroyed when the cluster is deleted.

After running the **cluster ssh** command simply navigate to http://loclahost:3000.

### Log in

To log in, use the username and password defined in the .env file. By default these are _username_: admin and _password_: password.

![Grafana login](./images/grafana_login.png)

### Configure a data source

After logging in you will need to configure a data source as shown below.

![Grafana data source](./images/datasource_setup.png)

### Importing the default dashboard

The default dashboard included in this plugin gives an overview of cluster health and is useful to see what the cluster is currently doing.

To import the dashbaord, click the '+' button on the left hand side and select 'import'.

![Grafana dashboard](./images/import_dashboard.png)

The sample configuration file can be found [here](./resource_monitor_dashboard.json).

Once you have imported the dashboard you can naviagte to the Perf Counters dashboard to view the cluster's data.

![Grafana dashboard](./images/default_dashboard.png)
