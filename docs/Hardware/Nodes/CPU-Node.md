## Adding, Replacing & Removing CPU Nodes

### Adding a CPU Node

See the [section about installing an OpenvCloud environment](../../Installation/Installation.md).

### Replacing a CPU node

Steps in order to replace a CPU node:

- **Step 1**: Put the node in Maintenance mode
  - Documented in the [section about putting a node in Maintenance mode](../../Sysadmin/Maintenance/putting_node_in_maintenance_mode.md)
  - Make sure to select the **Move All Virtual Machines** option:

    ![](confirm.png)

  - Wait until the node is in Maintenance mode, and that all virtual machines have moved to another node

- **Step 2**: Shutdown the node
- **Step 3**: Put the node in Decommission mode, documented [here](../../Sysadmin/Decommission/decommission_node.md)

- **Step 4**: Repair the node
- **Step 5**: Add the node back to the grid, following [installation documentation](../../Installation/Installation.md), more specifically the sections about [setting up the nodes](../../Installation/1-GetNodeInto911-mode.md) and [connecting them to the master cloud space](../../Installation/3-ConnectNode2ovc_git.md).



### Removing a CPU node

Same steps as above.
