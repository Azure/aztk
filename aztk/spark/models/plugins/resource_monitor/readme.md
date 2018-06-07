# Using the Resource Monitor Plugin

The resource monitor plugin is useful for tracking performance counters on the cluster. These include counters such as Percent CPU used per core, Disk Read, Disk Write, Network In, Network out, and several others. Simply enabling the plugin in your cluster.yaml will deploy all the necessary components to start tracking metrics.

This plugin takes advantage of the TICK monitoring stack. For more information please visit the [influx data](https://www.influxdata.com/time-series-platform/) web page.

> **IMPORTANT** All of the data is collected on the cluster's master node and will be lost once the cluster is thrown away. To persist data we recommend pushing to an off-cluster InfluxDB instance. Currently there is no supported way to persist the data from this plugin.

## Setup

Update your cluster.yaml file to include the plugin as follows:

```yaml
...

plugins:
  - name: resource_monitor

...


```

Once the cluster is created simply the cluster ssh command and all of the ports will automatically get forwarded.

```sh
aztk spark cluster ssh --id <my_cluster>
```

### Ports
url | description
--- | ---
http://localhost:8890 | Cronograf UI

## Visualize data in Chronograf

All data will automatically be published to the InfluxDB. In addition, this plugin also configures Chronograf to ingest the data for queries and visualization. After running **aztk spark cluster ssh --id <cluster_id>** navigate to http://localhost:8888 to open the UI.


### Host metrics
Each node (a.k.a. 'host' in Chronograf) in the cluster will register itself with the InfluxDB and start pushing metrics.
![Chronograf hosts](./images/chronograf_hosts.png)

Clicking on any individual host will give you more detail and historical metrics.

![Chronograf single host](./images/chronograf_single_host.png)

### Dashboards
Creating a dashboard is reasonably straight forward in Chronograf. Open up the dashboards panel.

![Chronograf create dashboard](./images/chronograf_create_dashboard.png)

Click on create new dashboard and add in the sources and metrics you wish to monitor.

![Chronograf build dashboard](./images/chronograf_build_dashboard.png)

>
> Much more information on using Chronograf is available on their official site at https://docs.influxdata.com/chronograf/
>


