## Connect Node to ovc_git

> **Note:** Do not run this script in paralllel in case of a remote (not Docker) node.

First make sure that you have the version tag environment variables set, specifying the versions of JS, AYS and OVC:
```
export JSBRANCH="7.0.2a"; export AYSBRANCH="7.0.2a" ; export OVCBRANCH="2.0.2a" ;

```

Then run the `pre-install.sh` script:
```
curl https://github.com/0-complexity/openvcloud/raw/master/scripts/install/pre-install.sh > /tmp/pre-install.sh
bash /tmp/pre-install.sh $REMOTEHOST
```

> **Note:** the name of the script is legacy, so it is no doing any real pre-installation, but rather just connects the node to `ovc_git`.

`$REMOTEHOST` must be the remote `ovc_git` hostname (or IP), e.g. `be-scale-1.demo.greenitglobe.com`

- In case of using Docker containers instead of virtual machines you have to specify the IP address of the Shuttle hosting the master cloud space.
- In case the Master Cloud Space is hosted at mothership1.com you have to specify the public IP address of the master cloud space.

When the script is done, your node should be ready for the next step: [Setup of Open vStorage](4-SetupOfOVS.md)

> **Note:** The scripts in what follows depend on the `service.hrd` files located at ```/opt/code/git/openvcloudEnvironments/$ENVIRONMENT/services/```. So, if you are re-using a repository, make sure that your reflector and other ip addresses are correct and are in place, or else you will not be able to connect to the tunnels.