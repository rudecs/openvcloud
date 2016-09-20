## Setup OS on the New Node

When the image is installed, connect to the node using SSH (default credential are: `gig/rooter`, you can `sudo -s` when logged in to be root).

There is a script which takes care of all the needed stuff to setup the node hardware, to apply it, just run (in root):

```
reboot
```

Wait for the machine to reboot.

Once rebooted connect again to the CPU node and fetch the **05-node-initializer.sh** script from the [0-complexity/openvcloud](https://github.com/0-complexity/openvcloud) GitHub repository.

Unfortunately you cannot simply curl this script into your environment yet because of the authentication, so navigate to the link, then copy and paste (vi) the content into your node:

```
curl https://github.com/0-complexity/openvcloud/raw/master/scripts/install/05-node-initializer.sh> /tmp/05-node-initializer.sh
. /tmp/05-node-initializer.sh
```

This will:
- Upgrade Ubuntu
- Detect used SSDs, build the partition schema
- Create and initialize Open vStorage (OVS) partitions
- Allow root SSH connection (root/rooter)
- Ensure that backplane1 is up
- Pre-install lots of OVS dependancies

Next you will want to connect the node to the **ovc_git** to set the reverse tunnel up.
