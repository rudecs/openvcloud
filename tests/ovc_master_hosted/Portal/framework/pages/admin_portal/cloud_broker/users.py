from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import leftNavigationMenu
import time
import uuid

class users():
    def __init__(self, framework):
        self.framework = framework
        self.LeftNavigationMenu = leftNavigationMenu(framework)

    def get_it(self):
        self.LeftNavigationMenu.CloudBroker.Users()

    def is_at(self):
        for temp in range(5):
            if self.framework.get_text("users_page") == "Users":
                return True
            else:
                time.sleep(0.5)
        else:
            return False

    def create_new_user(self, username='', password='', email='', group=''):
        username = username or str(uuid.uuid4()).replace('-', '')[0:10]
        password = password or str(uuid.uuid4()).replace('-', '')[0:10]
        email = email or str(uuid.uuid4()).replace('-', '')[0:10] + "@g.com"
        group = group or 'user'

        self.LeftNavigationMenu.CloudBroker.Users()

        self.framework.click("add_user")
        self.framework.assertTrue(self.framework.check_element_is_exist("create_user"))

        self.framework.set_text("username", username)
        self.framework.set_text("mail", email)
        self.framework.set_text("password", password)

        xpath_user_group = ''
        for i in range(1, 100):
            xpath_user_group = self.framework.elements["user_group"][1] % i
            if group == self.framework.driver.find_element_by_xpath(xpath_user_group).text:
                break
        user_group = self.framework.driver.find_element_by_xpath(xpath_user_group)
        if not user_group.is_selected():
            user_group.click()

        self.framework.click("confirm_add_user")
        self.framework.get_page(self.framework.driver.current_url)
        self.framework.set_text("username_search", username)
        self.framework.wait_until_element_located_and_has_text("username_table_first", username)
        self.framework.CLEANUP["users"].append(username)

    def open_user_page(self, username=''):
        username = username
        self.LeftNavigationMenu.CloudBroker.Users()

        self.framework.set_text("username_search", username)
        self.framework.wait_until_element_located_and_has_text("username_table_first", username)
        username_id = self.framework.get_text("username_table_first")

        self.framework.click("username_table_first")
        self.framework.wait_until_page_title_is('GBGrid - User')
        self.framework.element_in_url(username_id)

    def delete_user(self, username):
        self.LeftNavigationMenu.CloudBroker.Users()

        self.framework.set_text("user_search", username)
        self.framework.lg("check if this user is exist")
        if self.framework.wait_until_element_located_and_has_text("username_table_first",username):
            self.framework.lg("Delete %s user" % username)
            time.sleep(1)
            self.framework.assertEqual(self.framework.get_text("user_table_first_element"),username)
            self.framework.click("user_table_first_element")
            self.framework.assertEqual(self.framework.get_text("user_name")[6:],username)
            self.framework.click("user_action")
            self.framework.click("user_delete")
            self.framework.click("user_delete_confirm")
            self.framework.CLEANUP["users"].remove(username)
            return True
        else:
            self.framework.lg("There is no %s user" % username)
            return False
