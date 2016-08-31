# Capacity Limit Instrumentation

This document describes the implementation required to do capacity limiting on network disk and CPU.

## Actors

A new actor will be added under our private API `cloudbroker` which will be called `qos` (Quality of services)

### Methods that will be added

#### limitInternetBandwith

This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine

Params:
* cloudspaceId: Id of the cloudspace to limit
* maxSpeed: maximum speeds in kilobytes per second


#### limitInternalBandwith

This will put a limit on the VIF of all VMs within the cloudspace or machine
Pass either cloudspaceId or machineId depending what you want to filter down.


Params:
* cloudspaceId: Id of the cloudspace to limit
* machineId: Id of the virtual machine to limit
* maxSpeed: maximum speeds in kilobytes per second

#### limitIO

Params:
* diskId: Id of the disk to limit
* iops: Max IO per second

#### limitCPU

Params:
* machineId: Id of the VM
* maxload: ???
