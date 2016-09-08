### Grid Nodes

On the **Grid Nodes** page all nodes are listed:

![[]](GridNodes.png)

In the configuration shown above you see a grid of 5 nodes:
- **ovcmaster** has the **master** role, controlling the grid, and thus controlling all the other grid nodes
- **be-conv-2-01**, **be-conv-2-02**, **be-conv-2-03**, **be-conv-2-04** are all nodes with the **cpunode** and **storagenode**, physical machines combining storage and computing, this is where the actual virtual machines are running


From the **Grid Nodes** table you can navigate to the **Grid Node Details** page by clicking the name of the grid node:

![[]](GridNodeDetails.png)

#### CPU Statistics

Here the CPU usage and the system load is visualized:

![[]](CPUStatistics.png)

#### Info

In the **Info** section basic information about the grid is shown, including the roles and one or more IP addresses:

![[]](Info.png)

#### Statistics

From here you can navigate to all statistics for the selected node:

![[]](MoreStatistics1.png)
![[]](MoreStatistics2.png)

#### NICs

Here all NICs active on the node are listed:

![[]](NICs.png)

By clicking the name of a NIC you navigate to the **NIC Details** page:

![[]](NICDetails.png)

#### Jobs

This table lists the full jobs history for the node:

![[]](Jobs.png)

See the documentation of the [Jobs](../Jobs/Jobs.md) page for more information.

#### Machines

In the **Machines** table all virtual machines ever created on the node are listed:

![[]](Machines.png)

See the [Virtual Machines](../VirtualMachines/VirtualMachines.md) documentation for more information.

#### Logs

Here all the logs are listed for the node:

![[]](Logs.png)

See the [Logs](../Logs/Logs.md) documentation for more information.


#### Error Conditions

This table lists all error that occurred on the node:

![[]](ECOs.png)

See the [Error Conditions](../ErrorConditions/ErrorConditions.md) documentation for more information.

#### Disks

All disks on the selected node are listed here:

![[]](Disks.png)

By clicking the path you navigate to the **Disk Details** page:

![[]](DiskDetails.png)
