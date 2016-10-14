## Statistics

OpenvCloud integrates with [Grafana](http://grafana.org/) for data visualization, and uses [InfluxDB](http://docs.grafana.org/datasources/influxdb/) for storing all aggregated data gathered through **Redis** from various sources. See [How statistics are gathered](../Monitoring/Statistics/Statistics.md) for more details.

Actual visualization is done via **Grafana Dashboards** which are available in the **Operator Portal** under **Statistics**:

![](statistics.png)


### Overall System Performance

The **Cloud Broker Operator Portal** comes out of the box with the **Overall System Performance** dashboard consisting of following panels:
- [Total IOPS](#total-iops)
- [CPU utilization](#cpu-utilization)
- [CPU percentage](#cpu-percentage)
- [Available memory](#available-memory)
- [Context Switches](#context-switches)
- [Rx/Tx](#rx-tx)


<a id="total-iops"></a>
#### Total IOPS

![](Total-IOPS.png)


<a id="cpu-utilization"></a>
#### CPU utilization

![](CPU-Utilization.png)

![](CPU-Utilization-Table.png)


<a id="cpu-percentage"></a>
#### CPU percentage

![](CPU-Percentage.png)

![](CPU-Percentage-Table.png)


<a id="available-memory"></a>
#### Available memory

![](Available-Memory.png)

![](Available-Memory-Table.png)


<a id="context-switches"></a>
#### Context Switches

![](Context-Switches.png)
![](Context-Switches-Table.png)


<a id="rx-tx"></a>
#### Rx/Tx

![](Rx.png)
![](Tx.png)
