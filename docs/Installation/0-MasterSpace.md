## Installation of the Master Cloud Space

### Introduction

The first step to deploy an OpenvCloud environment is to setup the master cloud space.

The master cloud space is a collection of 4 virtual machines - or Docker containers:
- **ovc_git** holding all configuration of your environment
- **ovc_master** controlling the environment based on information from ovc\_git
- **ovc_reflector** provides [reverse SSH connections](https://en.wikipedia.org/wiki/Reverse_connection) to the physical nodes
- **ovc_proxy** running NGINX as a proxy for all port 80 and port 443 communications


The master cloud space can either be installed on
- [the Controller](#controller)
- [or any other physical or virtual machine](#ms1)

Both are documented here below.


<a id="controller"></a>
### Installing the master cloud space on the Controller

There are actually four steps:
- [Step 1: Bootstrap the installation](bootstrap)
- [Step 2: Create the ovc_git container](#ovc_git-container)
- [Step 3: Create all other containers](#other-containers)
- [Step 4: Set the password of the admin user](#password)


<a id="bootstrap"></a>
#### Bootstrap the installation (step 1)
To bootstrap the installation of the master cloud space, a temporary Docker container with all required components pre-installed is used. This container can be deleted afterwards.

Get access to one of the **Controllers** of your environment in order to run the temporary Docker container:

```
mkdir /opt/master_var
docker pull jumpscale/ubuntu1404
docker run -d --name=jumpscale jumpscale/ubuntu1404
```

(docker run -d -i -t --net=pxeboot --ip=10.21.2.124 --name=jumpscale jumpscale/ubuntu1404)

Use the `docker inspect` command in order to get the IP address of the Docker container:

```
docker ps
docker inspect jumpscale
```

Now start an SSH session using the IP address, e.g. `172.17.0.2`:

```
ssh root@172.17.0.2
```

In the container clone the [0-complexity/OpenvCloud](https://github.com/0-complexity/openvcloud) GitHub repository, here version/branch 2.1.5:

```
git clone -b 2.1.5 git@github.com:0-complexity/openvcloud.git
```

Before running the script you first need to update the version info that is hardcoded in the script:

```
JSBRANCH="7.1.5"
AYSBRANCH="7.1.5"
OVCBRANCH="2.1.5"
```

Run the **01-scratch-openvloud.sh** script:

```
cd openvcloud/scripts/install/
bash 01-scratch-openvcloud.sh
```

This script does the following:
- Install JumpScale
- Install Redis
- Install OpenvCloud
- Setup Git
- Install dependencies
- Check that all SSH keys are loaded


<a id="ovc_git-container"></a>
#### Create the ovc_git container (step 2)
Next get the **02-scratch-init.py** script from the [0-complexity/OpenvCloud](https://github.com/0-complexity/openvcloud) GitHub repository to do the actual work, creating the **ovc_git** container:

```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/install/02-scratch-init.py \
  --environment XXXX --git-user XXX --git-pass XXX \
  --backend docker \
  --backend docker --remote 172.17.0.1 --port 2375 --public XXX
```

You need to change content with your credentials:
- `environment` is the environment name (e.g.: be-conv-1, be-stor-1, du-conv-3, ...)
- `git-user` is your GitHub username
- `git-pass` is your GitHub password
- `domain` (optionally) is the domain name you will use, if omitted, demo.greenitglobe.com will be used
- `[ms1] user` is your Mothership1 username
- `[ms1] pass` is your Mothership1 password
- `[ms1] location` is the Mothership1 location of your cloud space (eu1, eu2, ...)
- `[ms1] cloudspace` is the name of the master cloud space at Mothership1, this is where **ovc_git** and all the other virtual machines will be created (useably, it's the same name of the environment)
- `[docker] remote` is the remote ip where Docker daemon is reachable
- `[docker] port` is the remote port where Docker daemon is reachable
- `[docker] public` is the public IP address from where the Docker container is reachable (host IP address)

To make to sure the Docker daemon listens to port 2375 you'll need to update the **/lib/systemd/system/docker.service** as follows, and restart Docker:

```
sudo vi /lib/systemd/system/docker.service
ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock
sudo systemctl restart docker.socket
sudo systemctl restart docker.service
```

And finally before actually executing the script make sure you've created a GitHub repository for your environment.

Once done, execute the script, here for instance for the environment uk-g8-1:

```
jspython 02-scratch-init.py --environment uk-g8-1 --backend docker --remote 172.17.0.1 --public 10.101.111.254
```

When this script has executed successfully, your **ovc_git** Docker container is ready. You can now ssh it, as mentioned in the output of the script.


<a id="other-containers"></a>
#### Create the other containers (step 3)

Make sure that when you ssh into **ovc_git** that you do this using the `-A` option, so that your private SSH keys get forwarded:

```
ssh root@localhost -p 2202 -A
```

When you are connected to it, you'll use the **03-ovcgit-master-spawn.py** script to deploy all the others virtual machines in the master cloud space of your environment. Also this script is available from the [0-complexity/OpenvCloud](https://github.com/0-complexity/openvcloud) GitHub repository.

To start it, first make sure the environment directory is your current directory (in this example 'env_gig'):

```
cd /opt/code/git/gig-projects/env_gig/
jspython 03-ovcgit-master-spawn.py --quiet
```

Then use the **04-ovcgit-master-configure.py** script to configure the network settings (IP addresses are fictitious examples), again make sure that the environment directory is your current directory:

```bash
cd /opt/code/git/gig-projects/env_gig/
jspython 04-ovcgit-master-configure.py --gateway 10.101.0.1 --start 10.101.101.100 --end 10.101.101.200 --netmask 255.255.0.0 --ssl wildcard --gid $RANDOM
```

Arguments are:
  ```
  --gateway  the IP address of the gateway
  --start    the IP address of the beginning of the public IP range
  --end      the IP address of the end of the public IP range
  --netmask  The netmask of the network
  --ssl      set [split|wildcard] to know which certificates to deploy
  --gid       Grid ID
  ```

For a demo.greenitglobe.com, `--ssl` option will always be "wildcard", for your domain it depends if you have a certificate per domain or a wildcard.

> # Note about certificates
>
> Your keys needs to be in the GitHub repository (protected) and need to follow the following format than demo.greenitglobe.com repository with your keys. The repository must be called: `certificates_[domain.tld]` with a `certs` folder on it. Your keys files **must** be named: `xxx-[env.domain.tld].crt` and `xxx-[env.domain.tld].key` (xxx is for ovs, defense, ... for split certificates)


From **ovc_git** you should be able to ssh to the other virtual machines in the master cloud space:

- ovc_reflector (`ssh reflector`)
- ovc_master (`ssh master`)
- ovc_dcpm (`ssh dcpm`)
- ovc_proxy (`ssh proxy`)


<a id="bootstrap"></a>
#### Set the password of the admin user (step 4)

Get on the ovc_master and set the password using **jsuser**:

```
ssh master -A
jsuser  passwd -ul $user -up $password
```


Your next steps will now be to [setup the nodes](1-GetNodeInto911-mode.md), and [connect them to the master cloud space](3-ConnectNode2ovc_git.md).
