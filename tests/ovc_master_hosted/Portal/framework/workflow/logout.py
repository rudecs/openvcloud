from pytractor.exceptions import AngularNotFoundException
import time


class logout():
    def __init__(self, framework):
        self.framework = framework

    def Admin_Logout(self):
        self.framework.lg('Do logout')
        self.framework.click('admin_logout_button')
        self.framework.lg('Logout done successfully')

    def End_User_Logout(self):
        self.framework.lg('Do logout')
        self.framework.click('drop_down_menu')
        self.framework.click('logout_button')
        self.framework.lg('Logout done successfully')