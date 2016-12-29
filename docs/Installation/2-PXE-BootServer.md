## Setup the OpenvCloud PXE Boot Server

@DRAFT
@NEEDS REVIEW


The OpenvCloud PXE boot server is available from the [0-complexity/G8OS_boot](https://github.com/0-complexity/G8OS_boot) GitHub repository. Follow the below steps in order to have it running in a Docker container on one of the Controllers.

Logged in on the Controller, make sure you're a user in the Docker group:

```bash
vigr # add you to the docker group
vigr -s # same
# log in again, or:
newgrp docker
```

Create a WORKDIR for your files, expand pxebootbinaries.tgz:

```bash
WORKDIR=$(pwd)/PXEDOCK
mkdir $WORKDIR
wget http://some.where.org/jumpscale/OVC/pxebootbinaries.tgz -O - | tar zxvf - -C ${WORKDIR}
```

We know have add a network for properly connecting to the management backend.

First, following commands create an Open vSwitch bridge named `pxeboot` and connects it to `backplane1` (optionally with a tag):

```bash
ovs-vsctl add-port backplane1 pxeboot [tag=2311]
# make sure it's up
ip l set pxeboot up
```

Then, create a Docker network with our Docker binary:

```bash
docker network create -d macvlan  --subnet=192.168.0.0/24 --gateway=192.168.0.1 -o parent=pxeboot pxeboot
```

What it does:

- use MACVLAN driver to create a network definition in Docker with name pxeboot
- and define gateway and network/mask

Run the Docker container:

```
cd ${WORKDIR}
docker run -it --rm --net=pxeboot --name=pxeboot -v $(pwd)/tftpboot:/tftpboot \
        --ip=192.168.0.240 \
               -v $(pwd)/conf:/conf \
               -v $(pwd)/images/vmlinuz-4:/tftpboot/vmlinuz-4 \
               -v $(pwd)/images/initrd.gz:/tftpboot/initrd.gz \
               --privileged jumpscale/pxeboot
```

What is does:

- bind-mount directory $tftpboot in docker /tftpboot
- same for conf
- bind-mount file $images/vmlinuz-4 as file in /tftpboot/vmlinuz-4
- same for initrd.gz

Further configuration is required:

- add a line `ip fqdn hostname` to `$(pwd)/hosts`
- add a line `ma:ca:dd:re-ss,hostname,infinite` to `$(pwd)/dhcphosts`
- configure `$(pwd)/conf/dnsmasq.conf` to reflect your network
  - changes to dnsmasq.conf need a restart of the docker
  - changes to hosts or dhcphosts needs just a SigHUP to the dnsmasq process

  ```bash
  PID=$(docker inspect --format '{{ .State.Pid}}' pxeboot)
  kill -HUP $PID
  ```
- make sure you have $(pwd)/images exposed as ftp or as http, where `$(pwd)/tftpboot/pxelinux.cfg/911boot` refers to the correct URL
- to boot a machine in 911, make a (sym)link from `$(pwd)/tftpboot/pxelinux.cfg/911boot` to `01-ma-ca-dd-re-ss-ss`:
  ```bash
  cd $(pwd)/tftpboot/pxelinux.cfg
  ln 911boot 01-ma-ca-dd-re-ss-ss
  ```
