from JumpScale import j
import JumpScale.portal
import JumpScale.baselib.http_client
import unittest

SESSION_DATA = {}

class ScenarioTest(unittest.TestCase):

    def setUp(self):
        cl = j.core.portal.getPortalClient(secret='1234')
        cl.getActor('cloud', 'cloudbroker')
        cl.getActor('cloudapi', 'accounts')
        cl.getActor('cloudapi', 'cloudspaces')
        cl.getActor('cloudapi', 'machines')
        cl.getActor('cloudapi', 'sizes')
        cl.getActor('cloudapi', 'images')
        self.brokerapi = j.apps.cloud.cloudbroker
        self.cloudapi = j.apps.cloudapi
        if 'stackid' in SESSION_DATA:
            self.brokerapi.stackImportImages(SESSION_DATA['stackid'])
            self.brokerapi.stackImportSizes(SESSION_DATA['stackid'])

    def test_1_CreateStack(self):
        stack = self.brokerapi.models.stack.new()
        stack.name = 'Dummy'
        stack.type = 'DUMMY'
        stack.login = 'admin'
        stack.passwd = 'rooter'
        stack.apiUrl = 'http://localhost/dummy/api'
        stackid = self.brokerapi.model_stack_set(stack.obj2dict())
        SESSION_DATA['stackid'] = stackid
        self.assertIsNotNone(stackid)

    def test_2_CreateProvider(self):
        resourceprovider = self.brokerapi.models.resourceprovider.new()
        resourceprovider.capacityAvailable = 100
        resourceprovider.cloudUnitType = 'CU'
        resourceprovider.stackId = SESSION_DATA['stackid']
        resourceprovider.referenceId = None
        resourceproviderid = self.brokerapi.model_resourceprovider_set(resourceprovider.obj2dict())
        SESSION_DATA['resourceproviderid'] = resourceproviderid
        self.assertIsNotNone(resourceproviderid)

    def test_3_CreateCustomer(self):
        accountid = self.cloudapi.accounts.create('testcustomer', ['admin'])
        SESSION_DATA['accountid'] = accountid
        self.assertIsNotNone(accountid)
        cloudspaceid = self.cloudapi.cloudspaces.create(accountid, 'testspace', ['admin'], maxMemoryCapacity=20480, maxDiskCapacity=2048)
        SESSION_DATA['cloudspaceid'] = cloudspaceid
        self.assertIsNotNone(cloudspaceid)

    def test_4_CreateMachine(self):
        sizeid = self.cloudapi.sizes.list()[0]
        imageid = self.cloudapi.images.list()[0]['id']
        machineid = self.cloudapi.machines.create(SESSION_DATA['cloudspaceid'], 'testmachine', 'test description', sizeid, imageid)
        SESSION_DATA['machineid'] = machineid
        self.assertIsNotNone(machineid)

def tearDownModule():
    cl = j.core.portal.getPortalClient(secret='1234')
    cl.getActor('cloud', 'cloudbroker')
    cl.getActor('cloudapi', 'accounts')
    cl.getActor('cloudapi', 'cloudspaces')
    brokerapi = j.apps.cloud.cloudbroker
    cloudapi = j.apps.cloudapi

    brokerapi.model_stack_delete(SESSION_DATA['stackid'])
    brokerapi.model_resourceprovider_delete(SESSION_DATA['resourceproviderid'])
    cloudapi.accounts.delete(SESSION_DATA['accountid'])
    cloudapi.cloudspaces.delete(SESSION_DATA['cloudspaceid'])
    brokerapi.model_vmachine_delete(SESSION_DATA['machineid'])

if __name__ == '__main__':
    unittest.main()
