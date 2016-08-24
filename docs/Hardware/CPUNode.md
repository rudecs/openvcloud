## Adding, Replacing & Removing CPU Nodes

### Adding a CPU Node

See the [section about installing an OpenvCloud environment](../Installation/Installation.md).


### Replacing a CPU node

Steps in order to replace a CPU node:

- Put the node in Maintenance mode, as documented in the [section about putting a node in Maintenance mode](../Sysadmin/Maintenance/putting_node_in_maintenance_mode.md)
  - Make sure to select the **Move All Virtual Machines** option:
  
    ![](confirm.png)

- Wait until the node is in Maintenance mode, and that all virtual machines have moved to another node
- Shutdown the node
- Then put the node in Decommission mode, as documented in the [section about decommissioning a node](../Sysadmin/Decommission/decommission_node.md)
- Repair the node
- Add the node back to the grid, following the steps documented in the [installation section](../Installation/Installation.md)


### Removing a CPU node

Same steps as above.



