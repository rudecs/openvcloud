import time
import uuid
from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import \
    leftNavigationMenu


class cloudspaces():
    def __init__(self, framework):
        self.framework = framework
        self.LeftNavigationMenu = leftNavigationMenu(framework)

    def get_it(self):
        self.LeftNavigationMenu.CloudBroker.CloudSpaces()

    def is_at(self):
        for _ in range(10):
            if 'Cloud Spaces' in self.framework.driver.title:
                return True
            else:
                time.sleep(1)
        else:
            return False

    def create_cloud_space(self, account, cloud_space=''):
        account = account
        self.framework.cloud_space_name = cloud_space or str(uuid.uuid4()).replace('-', '')[0:10]

        self.framework.Accounts.open_account_page(account)
        account_username = self.framework.get_text("account_first_user_name")

        self.framework.click("add_cloudspace")

        self.framework.assertEqual(self.framework.get_text("create_cloud_space"), "Create Cloud Space")

        self.framework.set_text("cloud_space_name", self.framework.cloud_space_name)
        self.framework.set_text("cloud_space_user_name", account_username)

        self.framework.click("cloud_space_confirm")
        self.framework.get_page(self.framework.driver.current_url)
        self.framework.set_text("cloud_space_search", self.framework.cloud_space_name)
        self.framework.wait_until_element_located_and_has_text("cloud_space_table_first_element_2",
                                                               self.framework.cloud_space_name)
        self.framework.lg(" %s cloudspace is created" % self.framework.cloud_space_name)
        return self.framework.cloud_space_name

    def open_cloudspace_page(self, cloudspace=''):
        cloudspace = cloudspace
        self.LeftNavigationMenu.CloudBroker.CloudSpaces()
        self.framework.set_text("cloud_space_search", cloudspace)
        self.framework.wait_until_element_located_and_has_text("cloud_space_table_first_element_2",
                                                               cloudspace)
        cloudspace_id = self.framework.get_text("cloud_space_table_first_element_1")
        self.framework.click("cloud_space_table_first_element_1")
        self.framework.wait_until_page_title_is('GBGrid - Cloud Space')
        self.framework.element_in_url(cloudspace_id)

    def delete_cloudspace(self, cloudspace=''):
        cloudspace = cloudspace

        self.framework.lg('open %s cloudspace' % cloudspace)
        self.open_cloudspace_page(cloudspace)

        for _ in range(50):
            if self.framework.get_text("cloudspace_page_status") in ["DEPLOYED", "VIRTUAL", "DESTROYED"]:
                break
            else:
                time.sleep(2)
                self.framework.get_page(self.framework.driver.current_url)
        else:
            self.framework.lg('"%s" cloudspace status : Deploying' % cloudspace)
            return False

        if self.framework.get_text("cloudspace_page_status") != "DESTROYED":
            self.framework.lg('start deleting "%s" cloudspace' % cloudspace)
            self.framework.click('cloudspace_action')
            if self.framework.get_text("cloudspace_page_status") == "DEPLOYED":
                self.framework.click('cloudspace_delete_deployed')
            elif self.framework.get_text("cloudspace_page_status") == "VIRTUAL":
                self.framework.click('cloudspace_delete_virtual')

            self.framework.set_text('cloudspace_delete_reason', "Test")
            self.framework.click("cloudspace_delete_confirm")
            self.framework.get_page(self.framework.driver.current_url)
            for temp in range(10):
                if self.framework.wait_until_element_located_and_has_text("cloudspace_page_status", "DESTROYED"):
                    return True
                else:
                    self.framework.get_page(self.framework.driver.current_url)
            else:
                self.framework.fail("Can't delete this '%s' cloudspcae")
        else:
            self.framework.lg('"%s" cloudspace is already deleted' % cloudspace)
            return True
