import time, signal, logging
from datetime import timedelta
from unittest import TestCase
from nose.tools import TimeExpired
from testconfig import config
from framework.api.client import Client
from framework.utils.utils import Utils
from testconfig import config

client_id = config['main']['client_id']
client_secret = config['main']['client_secret']

class TestcasesBase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = self.logger()

    @classmethod
    def setUpClass(cls):
        cls.api= Client(client_id=client_id, client_secret=client_secret)
        cls.utils = Utils()
        cls.whoami = config['main']['username']
        cls.environment =  cls.api.get_environment()
        cls.location = cls.environment['locationCode']
        cls.gid = cls.environment['gid']
        
    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()
        self.log.info('====== Testcase [{}] is started ======'.format(self._testID))
        self.user_api = Client()
        self.CLEANUP = {'users':[], 'accounts':[], 'groups':[], 'disks':[]}
        
        def timeout_handler(signum, frame):
            raise TimeExpired('Timeout expired before end of test %s' % self._testID)

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(540)

    def tearDown(self):
        self._endTime = time.time()
        self._duration = int(self._endTime - self._startTime)
            
        self.log.info('Testcase [{}] is ended, Duration: {} seconds'.format(self._testID, self._duration))

        for diskId in self.CLEANUP['disks']:
            self.log.info('[TearDown] Deleting disk: {}'.format(diskId))
            self.api.cloudapi.disks.delete(diskId=diskId)
        
        for accountId in self.CLEANUP['accounts']:
            self.log.info('[TearDown] Deleting account: {}'.format(accountId))
            self.api.cloudbroker.account.delete(accountId=accountId)

        for username in self.CLEANUP['users']:
            self.log.info('[TearDown] Deleting user: {}'.format(username))
            self.api.cloudbroker.user.delete(username=username)

    def logger(self):
        logger = logging.getLogger('OVC')
        if not logger.handlers:
            fileHandler = logging.FileHandler('testsuite.log', mode='w')
            formatter = logging.Formatter(' %(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)

        return logger