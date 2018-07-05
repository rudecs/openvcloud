import time

class AtYourService():

    def __init__(self, framework):
        self.framework = framework



class CloudBroker():
    def __init__(self, framework):
        self.framework = framework

    def Accounts(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_accounts")

    def CloudSpaces(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_cs")

    def Locations(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_locations")

    def Stacks(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_stacks")

    def Images(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_images")

    def PublicNetworks(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_public_nw")

    def Users(self):
        self.framework.open_base_page("cloud_broker", "cloudbroker_sub_users")

    def Groups(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_groups")

    def VirtualMachines(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_vm")

    def PhysicalNodes(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_physical_nodes")

    def ZeroAccess(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_0_access")

    def SoftwareVersions(self):
        self.framework.open_base_page("cloud_broker","cloudbroker_sub_sv")

class Statics():

    def __init__(self, framework):
        self.framework = framework



class Grid():

    def __init__(self, framework):
        self.framework = framework

    def error_conditions(self):
        self.framework.open_base_page("grid_arrow","error_conditions")

    def status_overview(self):
        self.framework.open_base_page("grid_arrow","status_overview")

class Storage():

    def __init__(self, framework):
        self.framework = framework



class Systems():

    def __init__(self, framework):
        self.framework = framework



class EndUser():

    def __init__(self, framework):
        self.framework = framework



class leftNavigationMenu():
    def __init__(self, framework):
        self.framework = framework

        self.CloudBroker = CloudBroker(self.framework)
        self.AtYourService = AtYourService(self.framework)
        self.Statics = Statics(self.framework)
        self.Grid = Grid(self.framework)
        self.Storage = Storage(self.framework)
        self.Systems = Systems(self.framework)
        self.EndUser = EndUser(self.framework)

    def compare_original_list_with_exist_list(self, menu_click, menu_element, original_list):
        self.framework.check_side_list()
        if menu_click != "":
            self.framework.click(menu_click)
        exist_menu = self.framework.get_list_items_text(menu_element)
        for item in original_list:
            if not item in exist_menu:
                self.framework.fail("This %s list item isn't exist in %s" % (item, exist_menu))

    def check_redirect_page(self, clickable_item, check_value):

        if clickable_item in ['system_sub_users','system_sub_sm', 'system_sub_api']:
            time.sleep(10)
        self.framework.check_side_list()
        self.framework.click(clickable_item)
        if self.framework.browser == 'firefox':
            time.sleep(2)
        self.framework.assertTrue(self.framework.element_in_url(check_value))
