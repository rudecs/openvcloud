## Update of the CPU Nodes

As is the case with updating the master cloud space, also in order to update all the CPU nodes you need to connect to the ovc_git of the environment which you like to upgrade. The actual updating happens from there.

- First, if not already done as part of updating the master cloud space, update the update script itself:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --self
```

- Then, again if not already done as part of updating the master cloud space, get all the cloned repositories updated:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --update
```

- Execute the following command to restart the services on the nodes:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --restart-nodes
```

- Alternatively to the previous step, you could combine a restart of the services on both the virtual machines in the master cloud space and nodes with one command:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --restart
```

Next you will want to [commit the changes and report back to the master repository](../CommitChanges/CommitChanges.md).