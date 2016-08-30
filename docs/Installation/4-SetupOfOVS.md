## Setup of Open vStorage

On `ovc_git` there is a script which will install everything needed on nodes for Open vStorage.

After having run the `pre-install.sh` script, go to the directory which contains your environment repository (example):

```bash
cd /opt/code/github/openvcloudEnvironments/be-dev-1/
```

From there you have two options:

- Use the auto-detection setup (highly recommended)
- Or use the the custom/manual setup


### Auto-detection setup

This is the simplest way to setup a basic OVS environment, if you are OK with the default configuration.

Just run this script as many time you have nodes:

```
jspython scripts/cpunode-setup.py
```

This auto-detection mode will:
- Search for an available node (sorted by name)
- Search if a OVS-master is already installed by the script
- If not, it will install the master OVS on the node-id you give, then save it
- If yes, it will install the slave node using the master already installed

> **Note:** this method will auto-detect master/slave for you. If you want a more custom method, please use the custom setup.

After the first node installation is done, you should have all the OVS and OVC packages downloaded into `/var/cache/apt/archives/*dep`, if you copied the packages in here to the other nodes, you shall cut the download time out of the installation .. you can do this with the following command

```bash
rsync -avzp --progress /var/cache/apt/archives/ root@IP_OF_THE_OTHERNODE://var/cache/apt/archives/
```
do this for all the nodes , note that you can use the internal ips of the nodes , which can be found in [here](https://git.aydo.com/openvcloudEnvironments/IP_Layout_DEMO/blob/master/Table.md)


### Custom setup

You can install the ovs-stuff using the same script as the auto-detect, but with some argument to make custom choice:
```
jspython scripts/cpunode-setup.py --node be-scale-1-01 --master
jspython scripts/cpunode-setup.py --node $XX --slave $IPMASTER
```

The node `$XX` should be replaced by node name (eg: envname-05, ...) and the `$IPMASTER` is the backplane master ip of the master node. The master install script should give you the IP address, it should be like: `10.xxx.1.11`

After that, your node is ready.

Next...