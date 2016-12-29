## Setup of Open vStorage

> For an introduction to Open vStorage you might first want to read the [Open vStorage documentation](https://openvstorage.gitbooks.io/administration/content/Openvstorage/).

On **ovc_git** you'll find the **07-ovcgit-cpunode-setup.py** script in order install all Open vStorage (OVS) components.

After having connected the node to **ovc_git** using the **06-node-connect.sh** script, documented in the the previous step [Connect Node to ovc_git](3-ConnectNode2ovc_git.md), go to the directory which contains your environment repository (example):

```bash
cd /opt/code/github/gig-projects/be-g8-1/
```

From there you have two options:

- [Use the auto-detection setup](#auto-detection) (**highly recommended**)
- [Or use the the custom/manual setup](#custom)

Both are discussed here below.

<a id="auto-detection"></a>
### Auto-detection setup

This is the simplest way to setup a basic OVS environment, if you are OK with the default configuration.

Just run **07-ovcgit-cpunode-setup.py** as many times as you have nodes:

```
jspython scripts/install/07-ovcgit-cpunode-setup.py
```

This auto-detection mode will:
- Search for an available nodes (sorted by name)
- Search if a OVS-master is already installed by the script
- If not, it will install the master OVS on the node-id you give, then save it
- If yes, it will install the slave node using the master already installed

> **Note:** this method will auto-detect master/slave for you. If you want a more custom method, please use the custom setup.

After the first node installation is done, you should have all the OVS and OVC packages downloaded into `/var/cache/apt/archives/*dep`. It is best to copy these packages to the other nodes, which will cut down the installation time:

```bash
rsync -avzp --progress /var/cache/apt/archives/ root@IP_OF_THE_OTHERNODE://var/cache/apt/archives/
```

Do this for all the nodes, note that you can use the internal ips of the nodes, which can be found in [here](https://git.aydo.com/openvcloudEnvironments/IP_Layout_DEMO/blob/master/Table.md)


<a id="custom"></a>
### Custom setup

You can install the Open vStorage using the same script as used with the auto-detection setup, but with some arguments to make custom choices:

```
jspython scripts/install/07-ovcgit-cpunode-setup.py --node be-scale-1-01 --master
jspython scripts/install/07-ovcgit-cpunode-setup.py --node $XX --slave $IPMASTER
```

`$XX` should be replaced by node name (e.g. envname-05) and `$IPMASTER` is the backplane master ip of the master node. The master install script should give you the IP address, it should be like: `10.xxx.1.11`.

After that, your node is ready.

Next...
