# Capacity Limit Instrumentation

This document describes the implementation required to do capacity limiting on network disk and cpu.

## Actors

A new actor will be added under our private api `cloudbroker` which will be called `qos` (Quality of services)

### Methods that will be added

#### limitBandwith

Params:
* cloudspaceId: Id of the cloudspace to limit
* maxSpeed: maximum speeds in kilobyts per second

#### limitIO

Params:
* machineId: Id of the virtual machine
* iops: Max IO per second

#### limitCPU

Params:
* machineId: Id of the virtual machine
* maxload: ???
