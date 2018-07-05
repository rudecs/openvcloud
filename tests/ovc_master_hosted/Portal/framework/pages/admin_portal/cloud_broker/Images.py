import time
import uuid
from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import \
    leftNavigationMenu


class images():
    def __init__(self, framework):
        self.framework = framework
        self.LeftNavigationMenu = leftNavigationMenu(framework)

    def get_it(self):
        self.LeftNavigationMenu.CloudBroker.Images()

    def is_at(self):
        for _ in range(10):
            if 'Images' in self.framework.driver.title:
                return True
            else:
                time.sleep(1)
        else:
            return False

    def open_image_page(self, image = None):
        self.LeftNavigationMenu.CloudBroker.Images()

        if image == None:
            table = self.framework.Tables.generate_table_elements('images')
            random_image = self.framework.Tables.get_random_row_from_table(table)
            image = random_image[0]

        self.framework.set_text("image_search", image)
        if self.framework.wait_until_element_located_and_has_text("image_table_first_element", image):
            self.framework.click('image_table_first_element')
            self.framework.wait_until_page_title_is('GBGrid - Image')
            return True
        else:
            self.framework.lg('can\'t find image %s' % image)
            return False
