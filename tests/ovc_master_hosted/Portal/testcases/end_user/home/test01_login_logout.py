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
        self.Login.Login()
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
        self.Login.Login()
        self.lg('check the home page title, should succeed')
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        self.lg('do logout, should succeed')
        self.Logout.End_User_Logout()
        time.sleep(5)
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')

    @parameterized.expand([('normal username', str(uuid.uuid4())),
                           ('long username', 'X'*1000),
                           ('numeric username', 9876543210),
                           ('special chars username', '+_=-)(*&^#@!~`{}[];\',.<>\/')])
    def test003_login_wrong_username(self, _, username):
        """ PRTL-003
        *Test case for check user potal login with wrong username.*

        **Test Scenario:**

        #. do login using wrong username, should fail
        #. proper error message, should succeed
        #. do login using admin username/password, should succeed
        #. check the home page title, should succeed
        #. do logout, should succeed
        #. check the login page title, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('do login using wrong , should succeed')
        self.Login.LoginFail(username=username)
        self.lg('do login using admin username/password, should succeed')
        self.Login.Login()
        self.lg('do logout, should succeed')
        self.Logout.End_User_Logout()
        time.sleep(5)
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        self.lg('%s ENDED' % self._testID)

    @parameterized.expand([('normal password', str(uuid.uuid4())),
                           ('long password', 'X'*1000),
                           ('numeric password', 9876543210),
                           ('special chars password', '+_=-)(*&^#@!~`{}[];\',.<>\/')])
    def test004_login_wrong_password(self, _, password):
        """ PRTL-004
        *Test case for check user potal login with wrong password.*

        **Test Scenario:**

        #. check the login page title, should succeed
        #. do login using wrong password, should fail
        #. proper error message, should succeed
        #. do login using admin username/password, should succeed
        #. check the home page title, should succeed
        #. do logout, should succeed
        #. check the login page title, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('do login using wrong , should succeed')
        self.Login.LoginFail(password=password)
        self.lg('do login using admin username/password, should succeed')
        self.Login.Login()
        self.lg('do logout, should succeed')
        self.Logout.End_User_Logout()
        time.sleep(5)
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        self.lg('%s ENDED' % self._testID)

    @parameterized.expand([('normal username/password', str(uuid.uuid4())),
                           ('long username/password', 'X'*1000),
                           ('numeric username/password', 9876543210),
                           ('special chars username/password', '+_=-)(*&^#@!~`{}[];\',.<>\/')])
    def test005_login_wrong_username_password(self, _, name):
        """ PRTL-005
        *Test case for check user potal login with wrong username/password.*

        **Test Scenario:**

        #. check the login page title, should succeed
        #. do login using wrong username/password, should fail
        #. proper error message, should succeed
        #. do login using admin username/password, should succeed
        #. check the home page title, should succeed
        #. do logout, should succeed
        #. check the login page title, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('do login using wrong , should succeed')
        self.Login.LoginFail(username=name, password=name)
        self.lg('do login using admin username/password, should succeed')
        self.Login.Login()
        self.lg('do logout, should succeed')
        self.Logout.End_User_Logout()
        time.sleep(5)
        self.assertEqual(self.driver.title, 'OpenvCloud - Decks')
        self.lg('%s ENDED' % self._testID)
