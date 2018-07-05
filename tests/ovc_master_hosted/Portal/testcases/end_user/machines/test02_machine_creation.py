from tests.ovc_master_hosted.Portal.framework.framework import Framework


class Read(Framework):
    def __init__(self, *args, **kwargs):
        super(Read, self).__init__(*args, **kwargs)

    def setUp(self):
        super(Read, self).setUp()
        self.Login.Login(cookies_login=True)
        self.EUMachines.create_default_account_cloudspace(self.admin_username, self.account, self.cloudspace)

    def tearDown(self):
        self.EUMachines.delete_default_account_cloudspace(self.account, self.cloudspace)
        self.Logout.Admin_Logout()
        super(Read, self).tearDown()


#     def test01_machine_get(self):
#         """
#         *Test case for get machine.*
#
#         **Test Scenario:**
#
#         #. create new machine, should succeed
#         #. get machine, should succeed
#         """
#
#     def test02_machine_list(self):
#         """
#         *Test case for list machine.*
#
#         **Test Scenario:**
#
#         #. create new machine, should succeed
#         #. list machines should see 1 machine, should succeed
#         """
#         pass
#
#     def test03_machine_getConsoleUrl(self):
#         """
#         *Test case for getConsoleUrl machine.*
#
#         **Test Scenario:**
#
#         #. create new machine, should succeed
#         #. getConsoleUrl machine, should succeed
#         """
#         pass
#
#     def test04_machine_listSnapshots(self):
#         """
#         *Test case for listSnapshots machine.*
#
#         **Test Scenario:**
#
#         #. create snapshot for a machine with the account user, should succeed
#         #. try to listSnapshots of created machine with new user [user], should return 403
#         #. add user to the machine with read access
#         #. listSnapshots of created machine with new user [user], should succeed
#         """
#         pass
#
#     def test05_machine_getHistory(self):
#         """
#         *Test case for getHistory machine.*
#
#         **Test Scenario:**
#
#         #. create new machine, should succeed
#         #. getHistory of created machine, should succeed
#         """
#         pass


    '''
    @parameterized.expand(["Ubuntu 16.04 x64",
                           "Ubuntu 15.10 x64",
                           "Windows 2012r2 Standard"
                           ])
    '''

    def test06_machine_create(self, image_name="Ubuntu 16.04 x64"):
        """ PRTL-011
        *Test case for creating/deleting machine with all avaliable image name, random package and random disk size*

        **Test Scenario:**

        #. create new machine, should succeed
        #. delete the new machine

        """
        self.lg('%s STARTED' % self._testID)
        self.lg(' create %s machine ' % self.machine_name)
        self.assertTrue(self.EUMachines.end_user_create_virtual_machine(image_name,self.machine_name))
        self.lg('delete %s machine ' % self.machine_name)
        self.assertTrue(self.EUMachines.end_user_delete_virtual_machine(self.machine_name))
        self.lg('%s ENDED' % self._testID)
