# Reservation of Host Memory

In certain situations it might be needed to reserve an extra amount of memory to the host of the CPU nodes. Reserved memory is memory that will not be available to allocate to virtual machines.

Configuration key: `reserved_mem`
Configuration value: `4096` (MB)


## Default values

Default values are dynamically generated depending on the host its physical memory:

- When the host has less then 64 GB of memory 1 GB is reserved
- When the host has less then 196 GB of memory 2 GB is reserved
- When the host has more then 196 GB of memory 4 GB is reserved
