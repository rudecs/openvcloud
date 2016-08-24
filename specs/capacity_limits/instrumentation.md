# Capacity Limit Instrumentation

This document describes the implementation required to do capacity limiting on network disk and cpu.

## Actors

A new actor will be added under our private api `cloudbroker` which will be called `qos` (Quality of services)

### Methods that will be added

#### limitInternetBandwith

This will put a limit on the outgoing traffic on the public vif off the vfw on the physical machine

Params:
* cloudspaceId: Id of the cloudspace to limit
* maxSpeed: maximum speeds in kilobyts per second


#### limitInternalBanwwith

This will put a limit on the virtual interface of all VMs within the cloudspace

Params:
* cloudspaceId: Id of the cloudspace to limit
* maxSpeed: maximum speeds in kilobyts per second

#### limitIO

Params:
* diskId: Id of the disk to limit
* iops: Max IO per second

#### limitCPU

Params:
* machineId: Id of the virtual machine
* maxload: ???
