# Reservartion of Host Memory

In certain situations it might be neeeded to reserve an extra amount of memory to the host of the cpu nodes.
Reserved memory is memory that will not be assigned to Virtual Machines.


configuration key: `reserved_mem`
configuration value: `4096` Value in MB

## Default Values:

Default values are dynamicly generated depending on the host its physical memory.
When the host has less then 64GB of memory 1GB is reserved
When the host has less then 196GB of memory 2GB is reserved
When the host has more then 196GB of memory 4GB is reserved
