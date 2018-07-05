import time
from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import \
    leftNavigationMenu


class physical_nodes():
    def __init__(self, framework):
        self.framework = framework
        self.LeftNavigationMenu = leftNavigationMenu(framework)

    def get_it(self):
        self.LeftNavigationMenu.CloudBroker.PhysicalNodes()

    def is_at(self):
        for _ in range(10):
            if 'PhysicalNodes' in self.framework.driver.title:
                return True
            else:
                time.sleep(1)
        else:
            return False

    
