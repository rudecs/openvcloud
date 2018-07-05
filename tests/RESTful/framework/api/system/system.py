from framework.api import utils
from framework.api.system.agentcontroller import AgentController
from framework.api.system.alerts import Alerts
from framework.api.system.audits import Audits
from framework.api.system.contentmanager import ContentManager
from framework.api.system.docgenerato import DocGenerator
from framework.api.system.emailsender import EmailSender
from framework.api.system.errorconditionhandler import ErrorConditionHandler
from framework.api.system.gridmanager import GridManager
from framework.api.system.health import Health
from framework.api.system.infomgr import InfoMgr
from framework.api.system.job import Job
from framework.api.system.log import Log
from framework.api.system.oauth import Oauth
from framework.api.system.task import Task
from framework.api.system.usermanager import UserManager

class System:
    def __init__(self, api_client):
        self.agentcontroller = AgentController(api_client)
        self.alerts = Alerts(api_client)
        self.audits = Audits(api_client)
        self.contentmanager = ContentManager(api_client)
        self.docgenerato = DocGenerator(api_client)
        self.emailsender = EmailSender(api_client)
        self.errorconditionhandler = ErrorConditionHandler(api_client)
        self.gridmanager = GridManager(api_client)
        self.health = Health(api_client)
        self.infomgr = InfoMgr(api_client)
        self.job = Job(api_client)
        self.log = Log(api_client)
        self.oauth = Oauth(api_client)
        self.task = Task(api_client)
        self.usermanager = UserManager(api_client)
