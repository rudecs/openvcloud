## Accounts

In order for a user to get access to actual cloud resources he needs to have access rights to an account.

The **Accounts** page lists all existing accounts:

![[]](Accounts.png)


### Creating Accounts

Creating a new account is simple. Just click on the **+ Add Account** link which will pop-up the **Create Account** window:

![[]](CreateAccount.png)

If the username you specify in the **Create Account** dialog doesn't exist yet, a new user will be created, and an activation email will be send to the email address you specify, allowing the user to set his password.

In case the username already exists, you can leave the e-mail address field empty, no activation e-mail will be send anyway.

The **Choose Location** (only shown in earlier versions) can be ignored, since accounts are always created cross-location.

All the next fields are related to maximum capacity available for the new account:

- **Memory Capacity** for limiting the total amount of memory (GB) that can be used by all cloud spaces in the account
- **VDisk Capacity** for limiting the total boot disk capacity (GB) used by all virtual machines created in the account
- **Number of CPU Cores** for limiting the total number of CPU cores used by all virtual machines created in the account
- **Primary Storage (NAS) Capacity** for limiting the total NAS disk capacity (TB) used by all virtual machines created in the account
- **Secondary Storage (Archive) Capacity** for limiting the total archive disk capacity (TB) used by all virtual machines created in the account
- **Network Transfer In Operator** for limiting the total internal network traffic (GB)
- **Network Transfer In Peering** for limiting the total public network traffic (GB)
- **Number of Public IP Address** for limiting the total number of cloud spaces that get a public IP address assigned

Once the account has been created it will appear in the accounts list, from which you can navigate to the **Account Details** page:

![[]](AccountDetails.png)

From there you:
- Rename an account
- Change the total available capacity
- Enable/Disable an account
- Delete an account
- Grant/revoke user access
- Add/remove/manage cloud spaces


### User Access

By default the user specified when creating a new account will have full access to the account:

![[]](GrantUserAccess.png)

You can grant other users access to the account by clicking the **+ Grant User Access** link, which will show the **Confirm Action Grant User Access** dialog:

![[]](ConfirmActionGrantUserAccess.png)

A user can have **read**, **write** or **admin** privileges. See the [End User Portal Authorization Model](../../EndUserPortal/Authorization/AuthorizationModel.md) documentation for all details on this.

- **Read**
 * Can access the **Getting Started**, **Machine API**, **Knowledge Base** and **Support** sections in the **End User Portal**
 * View account settings
 * Access/view the cloud space


- **Write**
 * All the above
 * Change account settings
 * Create cloud spaces


- **Admin**
 * All the above
 * Add users and set/change their access rights

For more information, check


### Cloud Spaces

All virtual data centers (cloud spaces) created in your account are listed here:

![[]](CloudSpaces.png)

The **+ Add Cloud Space** link allows you to add more cloud spaces to the account:

![[]](AddCloudSpace.png)

Again here you can specify limits for capacity that is available to the new cloud space.

From the list with cloud spaces you can navigate to the **Cloud Space Details** pages.

For more information on **Cloud Spaces** go to the [Cloud Spaces](../CloudSpaces/CloudSpaces.md) documentation.
