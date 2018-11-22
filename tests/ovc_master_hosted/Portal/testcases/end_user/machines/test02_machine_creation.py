from tests.ovc_master_hosted.Portal.framework.framework import Framework


class Read(Framework):
    def __init__(self, *args, **kwargs):
        super(Read, self).__init__(*args, **kwargs)

    def setUp(self):
        super(Read, self).setUp()
        self.Login.Login(cookies_login=True, portal='enduser')
        self.EUMachines.create_default_account_cloudspace(self.admin_username, self.account, self.cloudspace)

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
