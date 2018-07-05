import time, random
from testcases import *
from nose_parameterized import parameterized

class LibCloudBasicTests(TestcasesBase):

    def setUp(self):
        super().setUp()   
        response = self.api.cloudapi.locations.list()
        self.assertEqual(response.status_code, 200)

        locations = response.json()
        if not locations:
            self.skipTest('No locations were found in the environment')
        
        self._location = random.choice(locations)
        self.location = self._location['name'] 
        self.gid = self._location['gid']

    @parameterized.expand([('valid_gid', 200), ('invalid_gid', 400)])        
    def test01_get_free_mac_address(self, case, response_code):
        """ OVC-001
        #. Get free mac address, should succeed.
        #. Get free mac address of invalid grid id, should fail.
        """        
        if case == 'valid_gid':
            gid = self.gid
        else:
            gid = self.utils.random_string()

        response = self.api.libcloud.libvirt.getFreeMacAddress(gid=gid)
        self.assertEqual(response.status_code, response_code)

    @parameterized.expand([('valid_gid', 200), ('invalid_gid', 400)])
    def test02_get_free_network_id(self, case, response_code):
        """ OVC-002
        #. Get free network id, should succeed.
        #. Get free network id of invalid grid id, should fail.
        """
        if case == 'valid_gid':
            gid = self.gid
        else:
            gid = self.utils.random_string()

        response = self.api.libcloud.libvirt.getFreeNetworkId(gid=gid)
        self.assertEqual(response.status_code, response_code)

    @parameterized.expand([
            ('valid_newtwork_id', 200), 
            ('invalid_network_id', 409), 
            ('invalid_gid', 400),
            ('invalid_start', 400),
            ('invalid_end', 400),
        ])
    def test03_register_release_network_id_range(self, case, response_code):
        """ OVC-003
        #. Create account (AC1), should succeed.
        #. Create cloudspace (CS1), should succeed.
        #. Register network id, should succeed.
        #. Register network id in range of deployed networkids, should fail
        #. Register network id of invalid grid id, should fail.
        #. Register network id of invalid start value, should fail.
        """
        gid = self.gid
        start = random.randint(10000, 50000)
        end = start + 2

        if case in ['valid_newtwork_id', 'invalid_network_id']:

            self.log.info('Create account (AC1), should succeed')
            account_id = self.api.create_account()
            self.assertTrue(account_id)
            self.CLEANUP['accounts'].append(account_id)

            self.log.info('Create cloudspace (CS1), should succeed')
            cloudspace_id = self.api.create_cloudspace(accountId=account_id, location=self.location)
            self.assertTrue(cloudspace_id)

            response = self.api.cloudbroker.cloudspace.getVFW(cloudspaceId=cloudspace_id)
            self.assertEqual(response.status_code, 200)
            network_id = int(response.json()['id'])

            if case == 'invalid_network_id':
                start = network_id - 1
                end = network_id + 1

            self.log.info('Register network id, should succeed')
            data, response = self.api.libcloud.libvirt.registerNetworkIdRange(gid=gid, start=start, end=end)
            self.assertEqual(response.status_code, response_code)

        else:
            if case == 'invalid_gid':
                gid = self.utils.random_string()
            elif case == 'invalid_start':
                start = self.utils.random_string()
            elif case == 'invalid_end':
                end = self.utils.random_string()
                
            data, response = self.api.libcloud.libvirt.registerNetworkIdRange(gid=gid, start=start, end=end)
            self.assertEqual(response.status_code, response_code)

    @parameterized.expand([(3, False), (0, True)])
    def test04_store_retreive_info(self, timeout, reset):
        """ OVC-004
        #. Store info without timeout, should succeed.
        #. Retreive info, should succeed.
        #. Retreive info and reset, should succeed.
        #. Retreive info again, info should be null.
        #  Store info with timeout, should succeed.
        #. Retreive info before timeout, should useds.
        #. Retreive the info after the timeout, should be null.
        #. Store info with invalid timeout, should fail.
        """
        data = self.utils.random_string()

        self.log.info('Store info, should succeed')
        response = self.api.libcloud.libvirt.storeInfo(data=data, timeout=timeout)
        key = response.text.replace('"', '')
        self.assertEqual(response.status_code, 200)

        self.log.info('Retreive info, should succeed')
        response = self.api.libcloud.libvirt.retreiveInfo(key=key, reset=reset)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.replace('"', ''), data)

        if reset:
            self.log.info('Retreive info again, info should be null')
            response = self.api.libcloud.libvirt.retreiveInfo(key=key, reset=reset)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, 'null')

        if timeout:
            time.sleep(timeout + 1)
            self.log.info('Retreive the info after the timeout, should be null')
            response = self.api.libcloud.libvirt.retreiveInfo(key=key)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, 'null')
