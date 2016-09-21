## Installation of an OpenvCloud Environment

The installation is done through the usage of following installation scripts:

- 01-scratch-openvloud.sh
- 02-scratch-init.py
- 03-ovcgit-master-spawn.py
- 04-ovcgit-master-configure.py
- 05-node-initializer.sh
- 06-node-connect.sh
- 07-ovcgit-cpunode-setup.py
- 07-ovcgit-storagenode-setup.py
- 08-ovcgit-hardware-summary.py



All scripts are available from the [**\[0-complexity/OpenvCloud\]**](https://github.com/0-complexity/openvcloud) GitHub repository, where this is a **scripts/install** directory per version of OpenvCloud, i.e. **openvcloud/tree/2.1/scripts/install** in case of OpenvCloud v2.1.

Following naming format is used: [order]-[where-to-run]-[description].

There are three possibilities for [where-to-run]:

- **scratch** for scripts that can run somewhere from scratch, this is for the initialization/bootstrap scripts
- **ovcgit** for scripts that need to be run on **ovcgit**, with your current directory set to the environment repository
- **node** for scripts that need to be run on a CPU or storage node



The actual installation process takes 7 steps:

- [Installation of the Master Cloud Space](0-MasterSpace.md)
- [Have your nodes booted from an OpenvCloud PXE boot server](1-GetNodeInto911-mode.md)
- [Setup the OS on all the nodes](2-SetupOS.md)
- [Connect all the nodes to ovc_git](3-ConnectNode2ovc_git.md)
- [Setup Open vStorage](4-SetupOfOVS.md)
- [Configuration of Open vStorage](5-OVSConfiguration.md)
- [Post installation steps](6-PostInstallationSteps.md)
