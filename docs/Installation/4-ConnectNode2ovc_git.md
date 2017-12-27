## Connect Nodes to the ovc_git Container

Repeat the below on every single CPU and storage node.

Connecting a node to **ovc_git** is done using **06-node-connect.sh**.

From the controller ssh into the physical node:

```
ssh -A root@$IP-ADDRESS-OF-THE-NODE$
```

The IP addresses of all nodes can be found in **/opt/g8-pxeboot/pxeboot/conf/hosts**.

Once you are connected to the node, go to the **/tmp** directory and create the **branch.sh** file:

```
cd /tmp
vi branch.sh
```

In **branch.sh** you have to set the environment version variables, specifying the versions for JS, AYS and OVC, like this:

```
export JSBRANCH="production"
export AYSBRANCH="production"
export OVCBRANCH="production"
```

In order to make sure that you can reach the outside from node you might need to update the ***resolv.conf*** file:

```
vi /etc/resolv.conf
```

Add the Google DNS to it:

```
nameserver 8.8.8.8
```

Next you need to get the **06-node-connect.sh** script on the node:

```
wget https://raw.githubusercontent.com/0-complexity/openvcloud/master/scripts/install/06-node-connect.sh
```

Or:

```
curl https://github.com/0-complexity/openvcloud/raw/master/scripts/install/06-node-connect.sh > /tmp/06-node-connect.sh
```

Then run the **06-node-connect.sh** script:

```
bash /tmp/06-node-connect.sh $REMOTEHOST
```

`$REMOTEHOST` must be the remote **ovc_git** hostname (or IP), e.g. `be-scale-1.demo.greenitglobe.com`

- In case of using Docker containers instead of virtual machines you have to specify the IP address of the machine (typically a Controller) hosting the master cloud space.
- In case the master cloud space is hosted at mothership1.com you have to specify the public IP address of the master cloud space.


In order verify all went well, you can check on **ovc_git** the services directory:

```
/opt/code/github/gig-projects/env_uk-g8-1/services/jumpscale__location__uk-g8-1
```

For each node you'll find a subdirectory, here for instance for the first CPU node with hostname **cpu-01.cl-g8-uk1**:

```
jumpscale__node.ssh__cpu-01.cl-g8-uk1
```

When the script is done, your node should be ready for the next step: [Setup of Open vStorage](4-SetupOfOVS.md)
