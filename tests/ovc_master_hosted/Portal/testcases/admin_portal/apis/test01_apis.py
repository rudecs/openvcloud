from tests.ovc_master_hosted.Portal.framework.framework import Framework
import unittest


class APIsTests(Framework):
    def __init__(self, *args, **kwargs):
        super(APIsTests, self).__init__(*args, **kwargs)

    def setUp(self):
        super(APIsTests, self).setUp()
        self.Login.Login()
        self.EUMachines.create_default_account_cloudspace(self.admin_username, self.account, self.cloudspace)
        self.click("machine_api_button")


    @unittest.skip("bug: 178")
    def test01_list_images_using_account(self):
        """ PRTL-025
        *Test case for check list images using accountId is working.*

        **Test Scenario:**

        #. check list images without accountId, should succeed
        #. check list images with valid accountId, should succeed
        #. check list images with invalid accountId, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.click("cloudapi_images_show")
        self.click("cloudapi_images_list_btn")
        self.click("cloudapi_images_list_tryit")
        self.assertNotEqual(self.get_text("cloudapi_images_list_body"), "[]")
        self.set_text('cloudapi_images_list_accountid', 2)
        self.click("cloudapi_images_list_tryit")
        self.assertNotEqual(self.get_text("cloudapi_images_list_body"), "[]")
        self.set_text('cloudapi_images_list_accountid', 100000)
        self.click("cloudapi_images_list_tryit")
        self.assertEqual(self.get_text("cloudapi_images_list_body"), "[]")
        self.lg('%s ENDED' % self._testID)
