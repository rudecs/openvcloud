## Update an OpenvCloud Environment

It takes four majors steps in order to perform a full update of an OpenvCloud environment:

- [Update the Master Cloud Space](MasterCloudSpace/update_master_cloud_space.md)
- [Update All CPU Nodes](CPUNodes/update_cpu_nodes.md)
- [Commit Changes and Report Back](CommitChanges/CommitChanges.md)
- [Update Open vStorage](OVS/update_ovs.md)

Updating the master cloud space and all the CPU nodes (the first two steps) can be achieved with one script: `update-ays.py`.

It is however higly recommended not use to the `update-ays.py` script, and instead follow the above links, in order to have a more controlled execution.

So you will most probably want to read the [Update the Master Cloud Space](MasterCloudSpace/update_master_cloud_space.md) section.

For more information on `update-ays.py` click [here](update-ays.py.md). 