from tests.ovc_master_hosted.Portal.framework.framework import Framework


class AdminMenu(Framework):
    def __init__(self, *args, **kwargs):
        super(AdminMenu, self).__init__(*args, **kwargs)

    def setUp(self):
        super(AdminMenu, self).setUp()
        self.Login.Login(cookies_login=True)
        self.get_page(self.base_page)

    def test01_admin_menu_items(self):
        """ PRTL-022
        *Test case to make sure that the admin portal menu work as expected*

        **Test Scenario:**

        #. click on the admin menu
        #. verify all items
        #. for every main item verify its items and behavior
        #. for all items verify redirect page
        """

        compo_menu = ["Cloud Broker", "Statistics", "Grid", "Storage", "System", "End User"]
        cloud_broker_menu = ['Accounts', 'Cloud Spaces', 'Locations', 'Images', 'External Networks',
                             'Private Networks', 'Users', 'Groups', 'Virtual Machines', 'Software Versions']
        grid_menu = ['Audits', 'Error Conditions', 'Jobs', 'Job Queues', 'JumpScripts', 'Logs', 'Grid Nodes',
                     'Status Overview', 'Virtual Machines']

        storage_menu = self.get_storage_list()

        system_menu = ['Spaces', 'System Config', 'System Macros', 'Users', 'Groups', 'Code', 'API', 'Portal Logs',
                       'Access Overview']

        self.lg("check left menu")
        self.LeftNavigationMenu.compare_original_list_with_exist_list("", "left_menu", compo_menu)
        self.lg("check cloudbroker menu")
        self.LeftNavigationMenu.compare_original_list_with_exist_list("", "cloudbroker_menu",
                                                                      cloud_broker_menu)
        self.lg("check grid menu")
        self.LeftNavigationMenu.compare_original_list_with_exist_list("grid_arrow", "grid_menu", grid_menu)
        self.lg("check system menu")
        self.LeftNavigationMenu.compare_original_list_with_exist_list("system_arrow", "system_menu", system_menu)
        # self.lg("check storage menu")
        # self.LeftNavigationMenu.compare_original_list_with_exist_list("storage_arrow", "storage_menu", storage_menu)

        self.lg("check cloudbroker items redirect page")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_text", "cbgrid")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_accounts", "accounts")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_cs", "Cloud Spaces")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_locations", "locations")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_physical_nodes", "physicalnodes")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_images", "images")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_public_nw", "External Networks")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_private_nw", "private networks")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_users", "users")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_groups", "groups")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_vm", "Virtual Machines")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_0_access", "0-access")
        # in case user have no access to 0-access page back to the base page first
        self.get_page(self.base_page)
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_text", "cbgrid")
        self.LeftNavigationMenu.check_redirect_page("cloudbroker_sub_sv", "Version")

        # self.lg("check statistics items redirect page")
        # self.LeftNavigationMenu.check_redirect_page("statistics", "home/external")
        # self.get_page(self.base_page)

        self.lg("check grid items redirect page")
        self.LeftNavigationMenu.check_redirect_page("grid_text", "grid")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_audits", "Audits")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_ec", "Error Conditions")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_jobs", "Jobs")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_jq", "job queues")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_jumpsacale", "Jumpscripts")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_logs", "Logs")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_gn", "Grid Nodes")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_so", "Status Overview")
        self.LeftNavigationMenu.check_redirect_page("grid_sub_vm", "Virtual Machines")

        self.lg("check system items redirect page")
        self.LeftNavigationMenu.check_redirect_page("system_text", "system")
        self.LeftNavigationMenu.check_redirect_page("system_sub_spaces", "spaces")
        self.LeftNavigationMenu.check_redirect_page("system_sub_sc", "Systemconfig")
        self.LeftNavigationMenu.check_redirect_page("system_sub_sm", "systemmacros")
        self.LeftNavigationMenu.check_redirect_page("system_sub_users", "userlist")
        self.LeftNavigationMenu.check_redirect_page("system_sub_groups", "groups")
        self.LeftNavigationMenu.check_redirect_page("system_sub_code", "code")
        self.LeftNavigationMenu.check_redirect_page("system_sub_api", "actorsdocs")
        self.LeftNavigationMenu.check_redirect_page("system_sub_pl", "PortalLogs")
        self.LeftNavigationMenu.check_redirect_page("system_sub_ao", "overviewaccess")

        self.lg("check end user page")
        self.check_side_list()
        self.click("end_user")
        self.get_page(self.get_url())
        self.assertTrue(self.element_in_url('home'))
