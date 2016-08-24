## Get the Node into the 911 Mode

This is the first step in order to have an OpenvCloud environement set-up from scratch.

1. Prepare a **Controller** with the **OpenvCloud PXE boot server**.

   **OpenvCloud PXE boot server** is available from the GitHub [0-complexity/G8OS_boot](https://github.com/0-complexity/G8OS_boot) repository; also the installation and usage documentation is there.

2. Use the **Controller** to get the physical nodes boot in 911 mode.

   This mode gets a system in an OS-booted state where the whole OS is loaded into memory, with all tools available for install/recovery purposes. Once node is booted in 911 mode it is running Ubuntu 15.04 fully from memory, with SSH access enabled, and allowing you to use `apt-get` to install missing packages if needed.
   
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