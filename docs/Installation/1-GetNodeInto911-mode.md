## Get the Node into the 911 Mode

 The "911 mode" gets a system in a state where the whole OS is loaded into memory, with all tools available for install/recovery purposes. Once the node is booted in "911 mode" it is running Ubuntu 16.04 fully from memory, with SSH access enabled, and allowing you to use `apt-get` to install missing packages if needed.

On the controller you first need to start a Docker container running the **OpenvCloud PXE boot server**, which is available from the GitHub [0-complexity/G8OS_boot](https://github.com/0-complexity/G8OS_boot) repository; also the installation and usage documentation is there.

From the controller you will then enable the node to boot in "911 mode":
```
cd /opt/g8-pxeboot/pxeboot/scripts
enable-pxe $IP-address-of-the-node$  
```

OR hostnames from `/opt/g8-pxeboot/pxeboot/conf/hosts`?


Reboot:
```
ipmi-request $hostname chassis power cycle
```

....


If all done:

```
disable-pxe...
```



LEGACY:

   In `$PXEPATH/pxeboot/tftpboot/pxelinux.cfg/`, symlink the file `911boot` to `01-ma-ca-dd-re-ss-ss`.  

   If you have the BIOS of the physical node correctly set-up, the machine will load the NIX pxe code, request an IP, tftp the necessary files, and boot these instead of booting from local disk.


3. You should now be in the recovery (911) OS.

   Connect the machine using SSH (default credential are: `root/rooter`).

   To be sure, the prompt should be: `root@Installer`

   > **Note:** If, for whatever reason, you cannot find the gateway to the environment, you can also use the IPMI of the environment:

   - Reboot the node from the IPMI console
   - Chose 911 as the boot image from PXE menu
   - Credentials are `root/rooter`
   - Go to the tools directory: `/root/tools/`
   - Run the following on each node of the environment

     ```
     ./Install
     ```

     The installer will use the hostname the machine received to deduct the environment name, so make sure your `$PXEPATH/conf/*` files are correctly edited to your liking.
