
## Solution Blueprint

![](solution-blueprint.png)


### Controllers

Two or more small nodes installed local to the G8 physical nodes for managing/monitoring the G8 physical nodes.

Functions: 
- Boot/Install server driven by AYS
- AYS used to deploy all SW on nodes
- Monitoring services and collect statistics in the InfluxDB
- G8-Stor


### Nodes

There are two types of nodes:

- CPU/compute nodes
- Storage nodes

CPU/compute node functions: 
- Hypervisors
- Virtual machines
- Virtual networks
- Virtual routers
- Applications

Storage node fuctions:
- Storage (OVS)
- Alba (OVS)
- VSAN