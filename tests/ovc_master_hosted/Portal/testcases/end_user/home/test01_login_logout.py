import unittest
import uuid
from nose_parameterized import parameterized
from tests.ovc_master_hosted.Portal.framework.framework import Framework
import time

class LoginLogoutPortalTests(Framework):

    def test001_login_and_portal_title(self):
        """ PRTL-001
        *Test case for check user potal login and titles.*

        **Test Scenario:**

        #. check the login page title, should succeed
        #. do login using admin username/password, should succeed
        #. check the home page title, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('do login using admin username/password, should succeed')
        self.Login.Login(portal='enduser')
        self.lg('check the home page title, should succeed')
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        url = self.environment_url.replace('http:', 'https:')
        self.assertTrue(self.wait_element("machines_pic"))
        self.assertEqual(self.get_text("machines_label"),
                         "Configure, launch and manage your Virtual Machines. "
                         "Automate using the simple API.")
        self.assertEqual(self.element_link("machines_link"),
                        "%s/g8vdc/#/MachineDeck" % url)

    def test002_logout_and_portal_title(self):
        """ PRTL-002
        *Test case for check user potal logout and titles.*

        **Test Scenario:**

        #. check the login page title, should succeed
        #. do login using admin username/password, should succeed
        #. check the home page title, should succeed
        #. do logout, should succeed
        #. check the login page title, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('do login using admin username/password, should succeed')
        self.Login.Login(portal='enduser')
        self.lg('check the home page title, should succeed')
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        self.lg('do logout, should succeed')
        self.Logout.End_User_Logout()
        time.sleep(5)
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')