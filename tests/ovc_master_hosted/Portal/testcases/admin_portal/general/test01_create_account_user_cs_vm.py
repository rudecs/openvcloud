from tests.ovc_master_hosted.Portal.framework.framework import Framework
import time
class Account(Framework):
    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    def setUp(self):
        super(Account, self).setUp()
        self.Login.Login(cookies_login=True)

    def test01_create_account_user_cs_vm(self):
        """ PRTL-027
        *Test case for create new account, user, cloud space and Vm*

        **Test Scenario:**

        #. Create new user
        #. create new account
        #. open the account page
        #. create new cloudspace
        #. open cloudspace page
        #. create virtual machine
        #. open the virtual machine page
        #. delete this virtual machine page
        #. delete the cloudspcae
        #. delete the account
        #. delete the user
        """

        self.lg('Create new username, user:%s password:%s' % (self.username, self.password))
        self.Users.create_new_user(self.username, self.password, self.email, self.group)

        self.lg('open user page')
        self.Users.open_user_page(self.username)

        self.lg('create new account %s' % self.account)
        self.Accounts.create_new_account(self.account, self.username)

        self.lg('open the account page')
        self.Accounts.open_account_page(self.account)

        self.lg('create new cloudspace')
        self.CloudSpaces.create_cloud_space(self.account, self.cloudspace)

        self.lg('open cloud space page')
        self.CloudSpaces.open_cloudspace_page(self.cloudspace)

        self.lg('create virtual machine')
        self.VirtualMachines.create_virtual_machine(self.cloudspace, self.machine_name)

        self.lg('open virtual machine page')
        self.VirtualMachines.open_virtual_machine_page(self.cloudspace, self.machine_name)

        self.lg('delete virtual machine')
        self.VirtualMachines.delete_virtual_machine(self.cloudspace, self.machine_name)

        self.lg('delete cloudspace')
        self.CloudSpaces.delete_cloudspace(self.cloudspace)

        self.lg('delete account')
        self.Accounts.delete_account(self.account)

        self.lg('delete the user')
        self.Users.delete_user(self.username)
        self.lg('%s ENDED' % self._testID)
