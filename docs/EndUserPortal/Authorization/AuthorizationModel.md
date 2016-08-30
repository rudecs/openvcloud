## End User Portal Authorization Model

In order for a user to have access to the **End User Portal** group membership to the system group **user** is required. For more details about group membership, see the **Groups** page in the **Cloud Broker Portal** and the [Groups Documentation](../../CloudBrokerPortal/Groups/Groups.md).

Once access to the **End User Portal** actual privileges are determined by the rights (read, write, admin) granted to the user, this at the level of **Accounts**, **Cloud Spaces**, and **Virtual Machines**.

### Account

#### Read (R):

- account.get()
- account.list() (only accounts user has access to)
- account.getCreditBalance()
- account.getCreditHistory()

\+ ALL **Read** actions of **Cloud Space** and **Virtual Machine**

#### Write (RCX):

- ALL **Read** actions of **Account**

- cloudspace.create()
- machine.createTemplate()

\+ ALL **Read/Write** actions of **Cloud Space** and **Virtual Machine**

#### Admin (ARCXDU):

- ALL **Read/Write** actions of **Account**
- account.addUser()
- account.deleteUser()
- account.update()

\+ ALL **Admin/Write/Read** actions on **Cloud Space** and **Virtual Machine**


### Cloud Space

#### Read (R):

- cloudspace.get()
- cloudspace.list())(only the cloud spaces user has access to)
- machine.list()
- portforwarding.list() (for cloudspace)

\+ ALL **Read** actions of **Virtual Machine**

#### Write (RCX):

- ALL **Read** actions of **Cloud Space**
- cloudspace.deploy()
- cloudspace.getDefenseShield()
- machine.create()
- machine.importToNewMachine()
- portforwarding.create()
- portforwarding.delete()
- portforwarding.update() -> Change/delete port forwards for all virtual machines in this cloud space
- machine.clone()
- machine.delete()
- machine.addUser()
- machine.deleteUser()
- machine.updateUser()

\+ ALL **Read/Write** actions of **Virtual Machine**

#### Admin (ARCXDU):

- ALL **Read/Write** actions of **Cloud Space**
- cloudspace.addUser()
- cloudspace.updateUser()
- cloudspace.deleteUser()
- cloudspace.delete()
- cloudspace.update()

\+ ALL **Admin/Write/Read** actions of **Virtual Machine**


### Virtual Machine

#### Read (R):

- machine.get()
- machine.listSnapshots()
- machine.getConsoleUrl()
- machine.getHistory()
- machine.listExports()
- machine.list() (only for virtual machines user has access to)
- portforwarding.list() (for machine)

#### Write (RCX):

- ALL Read actions of Virtual Machine
- machine.addDisk()
- machine.backup()
- machine.snapshot()
- machine.rollbackSnapshot()
- machine.update()
- machine.export()
- machine.list() (only for virtual machines user has access to)
- machine.start()
- machine.stop()
- machine.pause()
- machine.resume()
- machine.reboot()
- machine.delDisk()
- machine.deleteSnapshot()
- portforwarding.add()
- portforwarding.delete()
- portforwarding.update()

#### Admin (ARCXDU):

\+ ALL **Write/Read** actions of **Virtual Machine**