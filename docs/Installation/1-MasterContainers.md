## Installation of the Master Containers

The master containers are actually 4 Docker containers:

- **ovc_git** holding all configuration of your environment
- **ovc_master** controlling the environment based on information from ovc\_git
- **ovc_reflector** providing [reverse SSH connections](https://en.wikipedia.org/wiki/Reverse_connection) to the physical nodes
- **ovc_proxy** running NGINX as a proxy for all port 80 and port 443 communications

The master containers are typically installed on one of the controllers, which takes four steps:

- [Step 1: Bootstrap the installation](#bootstrap)
- [Step 2: Create the ovc_git container](#git-container)
- [Step 3: Create all other containers](#other-containers)
- [Step 4: Set the password of the admin user](#password)

<a id="bootstrap"></a>
#### Bootstrap the installation (step 1)

To bootstrap the installation a temporary Docker container with all required components pre-installed is used. This container can be deleted afterwards.

Get access to one of the Controllers of your environment in order to run the temporary Docker container:

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

Now start an SSH session using the IP address, e.g. `172.17.0.2`, the default password is `gig1234`:

```
ssh root@172.17.0.2
```

In the container clone the [0-complexity/openvcloud](https://github.com/0-complexity/openvcloud) GitHub repository, here version/branch 2.1.5:

```
cd /opt/code/github/0-complexity/
git clone -b 2.1.5 git@github.com:0-complexity/openvcloud.git
```

First update the version info in the **01-scratch-openvloud.sh** script:

```
cd /opt/code/github/0-complexity/openvcloud/scripts/install
vim 01-scratch-openvloud.sh
```

For example use following values:

```
JSBRANCH="7.1.5"
AYSBRANCH="7.1.5"
OVCBRANCH="2.1.5"
```

Run the **01-scratch-openvloud.sh** script:

```
cd /opt/code/github/0-complexity/openvcloud/scripts/install
bash 01-scratch-openvcloud.sh
```

This script does the following:
- Install JumpScale
- Install Redis
- Install OpenvCloud
- Setup Git
- Install dependencies
- Check that all SSH keys are loaded


<a id="git-container"></a>
#### Create the ovc_git container (step 2)

Creating the ovc_git container is achieved by executing the **02-scratch-init.py** script from the temporary JumpScale container you created in the first step.

The **02-scratch-init.py** script takes following options:

- `-b`, `--backend`: possible values are `ms1` and `docker`
- `-G`, `--git-user`: GitHub username
- `-P`, `--git-pass`: GitHub password
- `-e`, `--environment`: environment name, for instance `be-test-1`
- `-d`, `--domain`: (optionally) the domain name, if not specified `demo.greenitglobe.com` will be used

In case you specified `docker` as backend (`--backend`) following additional options can be used:

- `-r`, `--remote`: IP address of the Docker engine used to create the Docker container
- `-o`, `--port`, port of on which the Docker engine is listening, default is 2375
- `-i`, `--public`, public IP address where of the **ovc_git** container, same as the IP address of the host (controller)

Or in case you specified `ms1` as backend (`--backend`) following additional options can be used:

- `-u`, `--user`: Mothership1 username
- `-p`, `--pass`: Mothership1 password
- `-c`, `--cloudspace`: cloud space on Mothership1 where the **ovc_git** virtual machine needs to be created
- `-l`, `--location`: Monthership1 location


Before actually executing the script make sure:

- You've created a GitHub repository for your environment
- In case you deploy on Docker, make sure the port on which the Docker engine (daemon) is listening (typically port 2375) is configured
  You can change it in `/lib/systemd/system/docker.service` as follows, and restart Docker:

  ```
  sudo vi /lib/systemd/system/docker.service
  ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock
  sudo systemctl restart docker.socket
  sudo systemc
  tl restart docker.service
  ```

So for instance to install the **ovc_git** container on the controller, use following command:

```
cd /opt/code/github/0-complexity/openvcloud/scripts/install
jspython 02-scratch-init.py --environment uk-g8-1 --backend docker --remote 172.17.0.1 --public 10.101.111.254
```

When this script has executed successfully, your **ovc_git** Docker container is ready. You can now ssh it, as mentioned in the output of the script.


<a id="other-containers"></a>
#### Create the other containers (step 3)

Make sure that when you ssh into **ovc_git** that you do this using the `-A` option, so that your private SSH keys get forwarded:

```
ssh root@localhost -p 2202 -A
```

When you are connected to it, you'll use the **03-ovcgit-master-spawn.py** script to deploy all the others containers.

To start it, first make sure the environment directory is your current directory (in this example 'env_gig'):

```
cd /opt/code/git/gig-projects/env_gig/
jspython 03-ovcgit-master-spawn.py --quiet
```

Then use the **04-ovcgit-master-configure.py** script to configure the network settings, again make sure that the environment directory is your current directory:

```
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


From **ovc_git** you should be able to ssh to the other containers:

- ovc_reflector (`ssh reflector`)
- ovc_master (`ssh master`)
- ovc_dcpm (`ssh dcpm`)
- ovc_proxy (`ssh proxy`)


<a id="password"></a>
#### Set the password of the admin user (step 4)

Get on the **ovc_master** and set the password using **jsuser**:

```
ssh master -A
jsuser  passwd -ul $user -up $password
```

Your next steps will now be to [install the OS on the nodes](1-InstallOS.md), and [connect them to ovc_git](3-ConnectNode2ovc_git.md).
