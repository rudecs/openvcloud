## Groups

Users need to be member of specific groups in order to have access to the OpenvCloud portals.

OpenvCloud comes with following predefined groups:

- **user** members have access to the **End User Portal**

  - **finance** members have access to the code **Consumption** information within the **End User Portal**

- **admin** members have access to the **At Your Service Portal**, **Cloud Broker Portal**, **Statistics Portal**, **Grid Portal** and **System Portal**

  - **level1** members can only use the "level 1" **Cloud Broker Portal** actions, which are (group per domain):

    - Accounts
      - Disabling accounts
      - Creating accounts
      - Enabling accounts
      - Renaming accounts
      - Deleting accounts
      - Adding users to an account
      - Deleting users from an account

    - Cloud Spaces
      - Create cloud spaces
      - Delete cloud spaces
      - Rename cloud spaces
      - Add users to a cloud space
      - Delete users from a cloud space
      - Delete Port Forwarding

    - Private Networks
      - Move virtual firewall to another node
      - Reset virtual firewall
      - Start virtual firewall
      - Stop virtual firewall
      - Remove virtual firewall
      - Deploy virtual firewall (only shown on the Cloud Space Details after having removed the firewall)
      - Add extra IP address (not exposed in default UI)
      - Remove IP address (not exposed in default UI)

    - Locations
      - Set status (not exposed in default UI)
      - Purge logs
      - Check virtual machines
      - Sync available images to Cloud Broker
      - Sync available sizes to Cloud Broker

    - Images
      - Delete images
      - Enable images
      - Disable images
      - Set image availability

    - Virtual machines
      - Create virtual machines
      - Create virtual machine on specific stack
      - Delete virtual machines
      - Start virtual machines
      - Stop virtual machines
      - Pause virtual machines
      - Resume virtual machines
      - Reboot virtual machines
      - Take snapshots of virtual machines
      - Rollback virtual machine to a snapshot
      - Delete snapshot of virtual machines
      - Clone virtual machines
      - Move virtual machine to another stack
      - Export virtual machines (not implemented)
      - Restore virtual machines
      - List exported virtual machines
      - Tag virtual machines
      - Untag virtual machines
      - List virtual machines
      - Check image chain of virtual machines
      - Stop virtual machines for abusive resource usage
      - Backup and destroy virtual machines
      - List snapshots of virtual machines
      - Get history of virtual machines
      - List port forwards of virtual machines
      - Create port forwards for virtual machines
      - Delete port forwards for virtual machines
      - Add disks to virtual machines
      - Delete disks from virtual machines
      - Create templates (images) of virtual machines (wich are saved to /mnt/vmstor/templates/...)
      - Update virtual machines
      - Attach virtual machines to public network
      - Detach virtual machines from public network

    - Users
      - Update password of users
      - Create users
      - Send reset password links to users
      - Delete users

  - **leve2** members can only use the "level 2" **Cloud Broker Portal** actions, which are currently only the following stack/node actions available in the **Stack Details** page:

    - **Put in Maintenance**
    - **Enable**
    - **Decommission**

  - **level3** members can only use the "level 3" **Cloud Broker Portal** actions

    > Today no "level 3" functions have been defined yet, so **level 1** membership will not yield any additional privileges to an administrative user

- **ovs_admin** members have access to the **Storage Portal**

On the **Groups** page all these standard groups are listed:

![[]](Groups.png)

From there you can navigate to the **Group Details** page of a group:

![[]](GroupDetails.png)

Under **Users** al users member of the group are listed:

![[]](Users.png)

By clicking the **ID** you navigate to the **User Details** page.

The **Actions** menu allows you to edit group properties or delete a group.

On the **Group** page you can also select **Add Group** from the **Actions** menu, allowing you to add/create your own groups. currently however you can't do much with this...
