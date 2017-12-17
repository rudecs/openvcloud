## Update the Master Cloud Space

The master cloud space typically runs on a docker inside the controller of the environment.

One of the containers in the master cloud space is ovc_git. This container is used to upgrade all the others virtual machines of the master cloud space, and all the physical CPU nodes that are managed by that master cloud space.

On ovc_git all OpenvCloud Git repositories are cloned, from which the updates are propagated in the environment.

- First step is to connect over SSH to ovc_git, as documented in the [How to Connect to an OpenvCloud Environment](../Sysadmin/connect.md) section.

- Login to the machine as root:
```bash
sudo -s
```

- Make sure you change the current directory to the directory where all cloned repositories reside of your environment, e.g. for environment du-conv-1:
```bash
cd /opt/code/github/gig-projects/env_du-conv-1/
```

- Check the history of the versions which were pulled from git:
```bash
git log
```
(press q to quit)

- Execute the following command to first update the update script itself:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --self
```

This will fetch the most recent version of the update script from the [0-complexity/OpenvCloud](https://github.com/0-complexity/openvcloud/) GitHub repository.

- Execute the following command to have all the cloned repositories updated:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --update
```

- Then restart the master cloud space:
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --restart-cloud
```

Read on: [Update the CPU Nodes](../CPUNodes/update_cpu_nodes.md)
