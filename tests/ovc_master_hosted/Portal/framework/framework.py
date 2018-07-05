from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.accounts import accounts
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.cloudspaces import cloudspaces
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.virtualmachines import virtualmachines
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.grid.error_conditions import errorConditions
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.grid.status_overview import statusOverview
from tests.ovc_master_hosted.Portal.framework.Navigation.left_navigation_menu import leftNavigationMenu
from tests.ovc_master_hosted.Portal.framework.Navigation.right_navigation_menu import rightNavigationMenu
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.users import users
from tests.ovc_master_hosted.Portal.framework.pages.end_user_portal.home import home
from tests.ovc_master_hosted.Portal.framework.pages.end_user_portal.machines import machines
from tests.ovc_master_hosted.Portal.framework.utils.utils import BaseTest
from tests.ovc_master_hosted.Portal.framework.workflow.login import login
from tests.ovc_master_hosted.Portal.framework.workflow.logout import logout
from tests.ovc_master_hosted.Portal.framework.workflow.tables import tables
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.Images import images
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.physical_nodes import physical_nodes
from tests.ovc_master_hosted.Portal.framework.pages.admin_portal.cloud_broker.zero_access import zero_access

class Framework(BaseTest):
    def __init__(self, *args, **kwargs):
        super(Framework, self).__init__(*args, **kwargs)

        #Pages.AdminPortal.Cloud_broker
        self.Users = users(self)
        self.Accounts = accounts(self)
        self.CloudSpaces = cloudspaces(self)
        self.VirtualMachines = virtualmachines(self)
        self.Images = images(self)
        self.PhysicalNodes = physical_nodes(self)
        #Pages.AdminPortal.grid
        self.ErrorConditions = errorConditions(self)
        self.StatusOverview = statusOverview(self)
        self.ZeroAccess = zero_access(self)

        #pages.end_user
        self.EUHome = home(self)
        self.EUMachines = machines(self)

        #NAvigation
        self.LeftNavigationMenu = leftNavigationMenu(self)
        self.RightNavigationMenu = rightNavigationMenu(self)

        #workflow
        self.Login = login(self)
        self.Logout = logout(self)
        self.Tables = tables(self)
