## Status Overview

The health of the system is monitored using a collection of JumpScripts, documented in [Monitoring the System Health](../../Monitoring/Health/Health.md).  

On the **Status Overview** page you get an immediate view on the health of the system.

You can access the **Status Overview** page in two ways:

- By clicking the green/orange/red status dot in the top navigation bar:

  ![](TopNavigation.png)

- or via the left navigation bar, under **Grid Portal** click **Status Overview**

Under the **Process Status** you get an overview of the health based on the last health check.

![](ProcessStatus.png)

By clicking **Run Health Check** a new health check gets scheduled to start immediately.

![](ConfirmActionRunHealthCheck.png)

Clicking any of the **Details** links brings you to the **Node Status** page, providing detailed health information for the selected node:

![](NodeStatus.png)

Clicking **Run Health Check on Node** will first ask you for your confirmation:

![](ConfirmActionRunHealthCheckOnNode.png)

Once confirmed all health check jobs (JumpScripts) will start, as you can verify on the **Jobs** page:

![](Jobs.png)

On the **Node Status** page you can see more details by clicking the various section titles. You also have the option here to start the health check related to any of them items listed under each of the sections.

Depending on the type of node, following sections are available:

| Section                       | Master Node | CPU Node | Storage Node |
|:------------------------------|:-----------:|:--------:|:------------:|
|[AYS Process](#ays-process)    | X           | X        | X            |
|[Databases](#databases)        | X           |          |              |
|[Disks](#disks)                | X           | X        | X            |
|[JSAgent](#jsagent)            | X           | X        | X            |
|[Network](#network)            | X           |          |              |
|[Orphanage](#orphanage)        | X           | X        |              |
|[Redis](#redis)                | X           | X        | X            |
|[System Load](#system-load)    | X           | X        | X            |
|[Temperature](#temperature)    | X           | X        | X            |
|[Workers](#workers)            | X           | X        | X            |
|[Hardware](#hardware)          |             | X        | X            |
|[Stack Status](#stack)         |             | X        |              |
|[Deployment Test](#deployment) |             | X        |              |
|[OVS Services](#ovs-services)  |             |          | X            |


<a id="ays-process"></a>
### AYS Process

![](AYSProcess.png)


<a id="databases"></a>
### Databases

![](Databases.png)


<a id="disks"></a>
## Disks

![](Disks.png)


<a id="jsagent"></a>
### JSAgent

![](JSAgent.png)


<a id="network"></a>
### Network

![](Network.png)


<a id="orphanage"></a>
### Orphanage

Depending on the node, you will see information about "orphan" disks or "orphan" virtual machines.

In case of the master node, this look like this:
![](OrphanDisks.png)

In case of a CPU node you will get an overview of all "orphan" virtual machines. This is about virtual machines that are marked as destroyed in the Grid and Cloud Broker Portal, while they still exist in reality on a physical node. This is obviously unwanted, and as part of automatic health checks, "orphan" virtual machines will get removed.

In order to manually remove "orphan" virtual machines use the following commands at the command line of the physical machine where the "orphan" virtual machine exists:

````shell
vm="vm-8"
disks="$(virsh dumpxml $vm | grep 'source file' | cut -d "'" -f 2)"
virsh destroy $vm; virsh undefine $vm
rm $disks
rm -rf /mnt/vmstor/$vm
````

<a id="redis"></a>
### Redis

![[]](Redis.png)


<a id="system-load"></a>
### System Load

![](SystemLoad.png)


<a id="temperature"></a>
### Temperature

![](Temperature.png)


<a id="workers"></a>
### Workers

![](Workers.png)


<a id="hardware"></a>
### Hardware

![](Hardware.png)


<a id="node"></a>
### Node Status

![](StackStatus.png)


<a id="deployment"></a>
### Deployment Test
![](DeploymentTests.png)


<a id="ovs-services"></a>
### OVS Services

![](OVSServices.png)
