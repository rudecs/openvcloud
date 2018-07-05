import time
import uuid
from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import leftNavigationMenu


class zero_access():
    def __init__(self, framework):
        self.framework = framework
        self.LeftNavigationMenu = leftNavigationMenu(framework)

    def get_it(self):
        self.LeftNavigationMenu.CloudBroker.ZeroAccess()

    def is_at(self):
        for _ in range(10):
            if '0-access' in self.framework.driver.title:
                return True
            else:
                time.sleep(1)
        else:
            return False

    def open_node_page(self, node=None):
        self.LeftNavigationMenu.CloudBroker.ZeroAccess()

        if not node:
            table = self.framework.Tables.generate_table_elements('zero_access_nodes')
            random_node = self.framework.Tables.get_random_row_from_table(table)
            node = random_node[0]

        self.framework.set_text("zero_access_nodes_search", node)
        if self.framework.wait_until_element_located_and_has_text("zero_access_nodes_first_element", node):
            self.framework.click('zero_access_nodes_first_element')
            return True
        else:
            self.framework.lg('can\'t find node %s' % node)
            return False


    def open_session_page(self, session=None):
        self.LeftNavigationMenu.CloudBroker.ZeroAccess()

        if not session:
            table = self.framework.Tables.generate_table_elements('zero_access_sessions')
            random_session = self.framework.Tables.get_random_row_from_table(table)
            session = random_session[0]

        self.framework.set_text("zero_access_sessions_search", session)
        if self.framework.wait_until_element_located_and_has_text("zero_access_sessions_first_element", session):
            self.framework.click('zero_access_sessions_first_element')
            return True
        else:
            self.framework.lg('can\'t find session %s' % session)
            return False
