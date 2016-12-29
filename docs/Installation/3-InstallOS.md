## Install the OS on the Physical Nodes

Before you continue, make sure that you installed and started on the controller a Docker container running the **OpenvCloud PXE boot server**, as documented in the [here](/Installation/2-PXE-BootServer.md).

For each of the physical nodes you need to execute the following three steps:

- [Boot node from the OpenvCloud PXE boot server](#911-mode)
- [Install the OS on the node](#install-os)
- [Disable PXE boot](#disable-PXE)

<a id="911-mode"></a>
### Boot node from the OpenvCloud PXE boot server

The "911 mode" gets a system in a state where the whole OS is loaded into memory, with all tools available for install/recovery purposes. Once the node is booted in "911 mode" it is running Ubuntu 16.04 fully from memory, with SSH access enabled, and allowing you to use `apt-get` to install missing packages if needed.

From the controller you will then enable the node to boot in "911 mode":

```
cd /opt/g8-pxeboot/pxeboot/scripts
enable-pxe $IP-address-of-the-node  
```

You can also specify the hostname of the physical node in stead of its IP address. The hostnames are in `/opt/g8-pxeboot/pxeboot/conf/hosts`.

Next you will reboot the node using `ipmi-request`:

```
ipmi-request $hostname chassis power cycle
```

<a id="install-os"></a>
### Install the OS on the node

Now the machine is in "911 mode", connect to it using SSH, with the default credential `root/rooter`. You should have the bash prompt `root@Installer`.

> **Note**: If for whatever reason, you cannot find the gateway to the environment, you can also use the IPMI of the environment:
>   - Reboot the node from the IPMI console
>   - Chose 911 as the boot image from the PXE menu

The actual installation is done using the `Install` script:

 ```
 cd /root/tools/
 ./Install
 ```

> **Note**: The installer will use the hostname the machine received to deduct the environment name, so make sure your `$PXEPATH/conf/*` files are all correctly edited.


<a id="disable-PXE"></a>
### Disable PXE boot

In order to make sure the node doesn't boot again in "911 mode" when restarting, you need to disable PXE booting:

```
disable-pxe $hostname
```
