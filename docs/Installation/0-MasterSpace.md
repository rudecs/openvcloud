## Installation of the Master Cloud Space

### Introduction

The first step to deploy an OpenvCloud environment is to setup the master cloud space. JumpScale provides tools to easily do this.

To bootstrap the installation of the master cloud space, you need to create the **ovc_git** virtual machine. This virtual machine will be used to install all the other virtual machines of the master cloud space.

> **Warning**: Please check or keep this in mind before starting:
- You must have a working **Redis** setup on your system
- You need write access to the **environment repository**, that is the GitHub repository that holds all configuration data of the environment, e.g. [gig-projects/env_gig](https://github.com/gig-projects/env_gig)
- You must have set your name and your e-mail address on your GitHub account
- Your system must have a working GitHub setup (email and name set)
- Your GitHub account needs to have access to all involved repositories (SSL offload, Racktivity, ...)

> If theses points are not respected, you will probably fail with some random errors.


Below following steps will be discussed in detail:
- [Step 1: Create the master cloud space](#master-cloud-space)
- [Step 2: Create ovc_git](#create-ovc_git)
- [Step 3: Create the other virtual machines](#other-machines)

<a id="master-cloud-space"></a>
### Create the master cloud space (step 1)

> **Note**: If this is a re-installation, you have to backup/delete the repository of the environment before proceeding.

The very first step is to setup a temporary virtual machine, from which we will be creating **ovc_git**:

1. Start with the creation of a new cloud space at Mothership1, this will be the master cloud space for your new environment

2. Create a temporary new virtual machine running Ubuntu, this machine can be deleted a afterwards, this machine must be on another cloud space

3. Verify whether the SSH authentication agents (ssh-agent) is running locally, using the -L option to get a list of the currently added keys:

   ```
   ssh-add -L
   ```

4. In case the authentication agent was not yet running, start it and add your keys, specifying the location of your private key, typically $HOME/.ssh/id_rsa:

   ```
   eval $(ssh-agent -s)
   ssh-add $LOCATION_OF_PRIVATEKEY
   ```

5. Then SSH into the temporary virtual machine, forwarding your current authentication agent connection by using the -A option:

   ```
   ssh -A remote -p port
   ```

   **Note**: If you are using a regular user (i.e. codescalers) to SSH into the temporary machine you have to use sudo in the following manner, so you do not lose your ssh key environment:

   ```
   sudo -E -s
   ```

6. On this temporary virtual machine, install JumpScale

> **Note:** You will have to set the environment variables [JSBRANCH + AYSBRANCH]to the specific tag(release) you want to install of JumpScale and OpenvCloud:

  ```
  export JSBRANCH="7.0.3"; export AYSBRANCH="7.0.3"; curl "https://raw.githubusercontent.com/jumpscale7/jumpscale_core7/${JSBRANCH}/install/install.sh" > /tmp/js7.sh && bash /tmp/js7.sh
  ```

7. Install Redis:

   ```
   ays install -n redis

   ```

8. Install the portal:

   ```
   ays install -n portal_lib
   ```

9. Install Python pip:

   ```
   apt-get install python-pip
   ```

**Notes:**

- There are no special requirements for the previous components, just choose the default values when asked or choose anything
- If for whatever reason you had a problem with tmux starting do the following:

  ```
  pkill -KILL tmux;rm -rf /tmp/tmux-*
  ```

Now you have a ready to go virtual machine to run the actual setup script, which will install the **ovc_git** machine from where all other virtual machines in the master cloud space will be created.

<a id="create-ovc_git"></a>
### Create ovc_git (step 2)

To perform the initial setup (deploying **ovc_git** which will be used for all the next setup), just run the **init.py** script in the OpenvCloud repository.

1. You have to clone the OpenvCloud repository, replace **<version>** with the specific version/tag you want to use, e.g. "2.0.2a":

  ```
  mkdir -p /opt/code/github/0-complexity/
  cd /opt/code/github/0-complexity/
  git clone -b <version> git@github.com:0-complexity/openvcloud.git
  ```

2. You have to configure an email and username for the git to work on the bootstrap machine:

  ```
  git config --global user.name "example@example.com"
  git config --global user.email "username"
  ```

Depending on where you are deploying the master cloud space, click the instructions for:
- [Deploying the master cloud space at Mothership1 (using virtual machines)](#ms1)
- [Deploying locally (typically on the **Controllers**) using Docker containers](#controller)

<a id="ms1"></a>
#### Deploying the master cloud space at Mothership1 (using virtual machines)

  ```bash
  jspython /opt/code/github/0-complexity/openvcloud/scripts/install/init.py \
    --environment XXXX --git-user XXXX --git-pass XXXX \
    --backend ms1 \
    --cloudspace XXX --location eu2 --user XXX --pass XXX
  ```
<a id="controller"></a>
#### Deploying locally (typically on the **Controllers**) using Docker containers

1. Edit **atyourservice.hrd**:

   ```
   vim /opt/jumpscale7/hrd/system/atyourservice.hrd
   ```

   Make sure to point to the correct branch of the the **openvcloud_ays** repository:

   ```
   metadata.openvcloud            =
      branch:'2.0.2',
      url:'https://github.com/0-complexity/openvcloud_ays',
   ```

   Verify that your private SSH key is loaded:

   ```
   ssh-add -l
   ```

   You can edit this file

   ```
   /opt/jumpscale7/hrd/system/whoami.hrd
   ```

   And make sure that the content are like wise:

   ```
   git.login                      = ssh
   git.passwd                     = ssh
   ```

2. Edit **docker**

   ```
   vim /etc/default/docker
   ```

   Make sure that **DOCKER_OPTS** has the following value:

   ```
   DOCKER_OPTS="-H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375"
   ```

> **Notes**:
1. Please use the latest Docker version ( >= 1.10 )
2. If you are doing a reinstall, make sure you remove all the Docker containers and also the contents of `/opt/master_var`


#### Docker (local) backend
```bash
jspython /opt/code/github/0-complexity/openvcloud/scripts/install/init.py \
  --environment XXXX --git-user XXX --git-pass XXX \
  --backend docker \
  --backend docker --remote 172.17.0.1 --port 2375 --public XXX
```

You need to change content with your credentials:
- `environment` is the environment name (e.g.: be-conv-1, be-stor-1, du-conv-3, ...)
- `git-user` is your GitHub username
- `git-pass` is your GitHub password
- `domain` is optionally the domain name you will use, if omitted, demo.greenitglobe.com will be used
- `[ms1] user` is your Mothership1 username
- `[ms1] pass` is your Mothership1 password
- `[ms1] location` is the Mothership1 location of your cloud space (eu1, eu2, ...)
- `[ms1] cloudspace` is the name of the master cloud space at Mothership1, this is where ovc_git and all the other virtual machines will be created (useably, it's the same name of the environment)
- `[docker] remote` is the remote ip where docker daemon is reachable
- `[docker] port` is the remote port where docker daemon is reachable
- `[docker] public` is the public ip from where the docker is reachable (host ip)


When this script has executed successfully, your **ovc_git** virtual machine is ready. You can now ssh it, as mentioned in the output of the script.


<a id="other-machines"></a>
### Create the other virtual machines (step 3)

Make sure that when you ssh into **ovc_git** that you do this with an `ssh -A ovc_git`, so that you agent forwarding is active and the **aio.py** is successful when cloning repositories and creating other machines needed for the master cloud space.

When you are connected to it, there is another script to be executed which will deploy all the others virtual machines in the master cloud space of your environment.

To start it, at first, go to the environment directory, which was cloned from the environment repository (in this example 'env_gig'):

```
cd /opt/code/git/gig-projects/env_gig/
```

First use the **master-spawn.py** script for creating the required virtual machines and configure them:

```
jspython scripts/master-spawn.py --quiet
```

Then use the **master-configure.py** script to configure the network settings (IP addresses are fictitious examples):

```bash
jspython scripts/master-configure.py --gateway 10.101.0.1 --start 10.101.101.100 --end 10.101.101.200 --netmask 255.255.0.0 --ssl wildcard --gid $RANDOM
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

Your next steps will now be to [setup the nodes](1-GetNodeInto911-mode.md), and [connect them to the master cloud space](3-ConnectNode2ovc_git.md).
