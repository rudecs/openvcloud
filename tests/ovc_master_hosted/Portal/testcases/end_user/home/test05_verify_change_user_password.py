import unittest
import uuid
from tests.ovc_master_hosted.Portal.framework.framework import Framework

@unittest.skip('users created from admin portal cannot be accessed from itsyou.online')
class ChangePassword(Framework):
    def __init__(self, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
    def setUp(self):
        super(ChangePassword, self).setUp()
        self.Login.Login(cookies_login=True, portal='enduser')

    def test01_verify_change_user_password(self):
        """ PRTL-022
        *Test case for create new user and change his password*

        **Test Scenario:**
        #. Create new user
        #. Login using this user
        #. Change his password
        #. Logout
        #. Login using this user and the new password
        #. Logout
        #. Login as admin
        #. Delete this user
        """
        self.lg('%s STARTED' % self._testID)
        self.username = str(uuid.uuid4()).replace('-', '')[0:10]
        self.password = str(uuid.uuid4()).replace('-', '')[0:10]
        self.email = str(uuid.uuid4()).replace('-', '')[0:10] + "@g.com"
        self.group = 'user'

        self.lg('Create new username, user:%s password:%s' % (self.username, self.password))
        self.Users.create_new_user(self.username, self.password, self.email, self.group)
        self.driver.ignore_synchronization = False

        self.Logout.Admin_Logout()

        self.lg("login using the new username")
        self.driver.get(self.get_url())
        self.Login.Login(self.username, self.password)

        self.lg("check access denied")
        if self.check_element_is_exist("access_denied"):
            self.driver.get(self.environment_url)

        self.lg("Change the password")
        self.click("user_profile")
        self.set_text("current_pw", self.password)
        self.newPassword = str(uuid.uuid4()).replace('-', '')[0:10]
        self.set_text("new_pw_1", self.newPassword)
        self.set_text("new_pw_2", self.newPassword)
        self.click("update_password")

        self.lg("Do logout")
        self.Logout.End_User_Logout()
        self.driver.get(self.get_url())

        self.lg("Login using new password")
        self.Login.Login(self.username, self.newPassword)
        self.driver.get(self.environment_url)
        self.click("user_profile")
        self.assertEqual(self.get_text("profile"), "Profile")

        self.lg("Do logout")
        self.click("end_user_logout")
        self.lg('%s ENDED' % self._testID)
