# Multiple vpools

In Open vStorage Fargo release it is advisable to create multiple vpools to be able to run more volumedriver instances per storage node. Each volumedriver instance can serve up to 125k iops but not more than that. So to be able to get more than 125k iops from one OVS node we need to be able to cope with more than one vpool.

## vmstor vpool

The vmstor vpool wil be used for bootdisks only. This way we do not need to make bootdisk templates available on all vpools.

## data## vpool

Depending on the size of the storage setup we will create 1 or more vpools that will be used for datadisks. eg:
- data01
- data02
- data03
- ...

## spreading

Data disks will be provisioned over the different data## vpools using a simple round-robin mecanisme.
At the same time vdisks need to be spread over the different storage routers of a vpool also via a round robin mechanisme (also for boot and routeros disks).
