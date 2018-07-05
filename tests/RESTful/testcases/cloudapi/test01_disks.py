import time, random, unittest
from testcases import *
from nose_parameterized import parameterized

class PermissionsTests(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.log.info('Create users (U2) with admin access')
        self.admin_api, self.admin = self.api.authenticate_user(groups=['admin'])
        self.log.info('Create users (U3) with user access')
        self.user_api, self.user = self.api.authenticate_user(groups=['user']) 
        self.CLEANUP['users'].extend([self.admin, self.user])
        
        self.log.info('Create Account (A1) using user (U1)')
        self.account_id = self.api.create_account()
        self.assertTrue(self.account_id)
        self.CLEANUP['accounts'].append(self.account_id)
        
        self.log.info('create disk on account (A1) using user (U1), should succeed')
        self.disk_data, self.response = self.api.cloudapi.disks.create(accountId=self.account_id, gid=self.gid)
        self.assertEqual(self.response.status_code, 200, self.response.content)        
        self.diskId = int(self.response.text)

    def tearDown(self):
        self.api.cloudapi.disks.delete(diskId=self.diskId)
        super().tearDown()

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test01_create_disk(self, role, response_code):
        """ OVC-001
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try create disk on account (A1) using user (U2), should succeed. 
        #  Try create disk on account (A1) using user (U3), should fail.         
        """
        self.log.info('Try create disk on account (A1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        api = self.admin_api if role == 'admin' else self.user_api
        data, response = api.cloudapi.disks.create(accountId=self.account_id, gid=self.gid)
        self.assertEqual(response.status_code, response_code, response.content)
        
        if role == 'admin':
            self.CLEANUP['disks'].append(int(response.text))

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test02_list_disks(self, role, response_code):
        """ OVC-002
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try to list account (A1)'s disks using user (U2), should succeed. 
        #  Try to list account (A1)'s disks using user (U3), should fail.         
        """
        self.log.info('Try to list account (A1)\'s disks using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.disks.list(accountId=self.account_id)
        self.assertEqual(response.status_code, response_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test03_get_disk(self, role, response_code):
        """ OVC-003
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try to get disk (D1) using user (U2), should succeed. 
        #  Try to get disk (D1) using user (U3), should fail.         
        """
        self.log.info('Try to get disk (D1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.disks.get(diskId=self.diskId)
        self.assertEqual(response.status_code, response_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test04_resize_disk(self, role, response_code):
        """ OVC-004
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try to resize disk (D1) using user (U2), should succeed. 
        #  Try to resize disk (D1) using user (U3), should fail.         
        """
        self.log.info('Try to resize disk (D1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        size = self.disk_data['size'] + random.randint(1, 20)        
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.disks.resize(diskId=self.diskId, size=size)
        self.assertEqual(response.status_code, response_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test05_delete_disk(self, role, response_code):
        """ OVC-005
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try to delete disk (D1) using user (U2), should succeed. 
        #  Try to delete disk (D1) using user (U3), should fail.         
        """
        self.log.info('Try to delete disk (D1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.disks.delete(diskId=self.diskId)
        self.assertEqual(response.status_code, response_code, response.content)
    
    @parameterized.expand([('admin', 200), ('user', 403)])
    def test06_limit_disk_io(self, role, response_code):
        """ OVC-006
        #. Create users (U1) & (U2) with admin access.
        #. Create user (U3) with user access.
        #  Create Account (A1) using user (U1).
        #  Try to limit disk (D1) io using user (U2), should succeed. 
        #  Try to limit disk (D1) io using user (U3), should fail.         
        """
        self.log.info('Try to limit disk (D1) io using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        api = self.admin_api if role == 'admin' else self.user_api
        data, response = api.cloudapi.disks.limitIO(diskId=self.diskId)
        self.assertEqual(response.status_code, response_code, response.content)

class OperationTests(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.account_id = self.api.create_account()
        self.assertTrue(self.account_id)
        self.CLEANUP['accounts'].append(self.account_id)
        self.disk_data, self.response = self.api.cloudapi.disks.create(accountId=self.account_id, gid=self.gid)
        self.assertEqual(self.response.status_code, 200, self.response.content)        
        self.diskId = int(self.response.text)

    def tearDown(self):
        self.api.cloudapi.disks.delete(diskId=self.diskId)
        super().tearDown()
    
    @parameterized.expand([
        ('exists_account', 200), 
        ('non_exists_account', 404), 
        ('invalid_account', 400)
    ])
    def test01_list_disks(self, case, response_code):
        """ OVC-001
        #. Create Account (A1), should succeed.
        #. Create disk (D1), should succeed.
        #. List account (A1) disks, (D1) should be listed. 
        """
        account_id = self.account_id

        if case == 'non_exists_account':
            account_id = random.randint(100000, 200000)
        elif case == 'invalid_account':
            account_id = self.utils.random_string()

        response = self.api.cloudapi.disks.list(accountId=account_id)
        self.assertEqual(response.status_code, response_code, response.content)

        if case == 'exists_account':
            self.assertIn(self.diskId, [disk['id'] for disk in response.json()])

    @parameterized.expand([
        ('exists_disk', 200), 
        ('non_exists_disk', 404),
        ('invalid_disk', 400)
    ])
    def test02_get_disk(self, case, response_code):
        """ OVC-001
        #. Create Account (A1), should succeed.
        #. Create disk (D1), should succeed.
        #. List account (A1) disks, (D1) should be listed. 
        """
        diskId = self.diskId

        if case == 'non_exists_disk':
            diskId = random.randint(100000, 200000)
        elif case == 'invalid_disk':
            diskId = self.utils.random_string()

        response = self.api.cloudapi.disks.get(diskId=diskId)
        self.assertEqual(response.status_code, response_code, response.content)

        if case == "exists_disk":
            self.assertEqual(response.json()['name'], self.disk_data['name'])
            self.assertEqual(response.json()['descr'], self.disk_data['description'])
            self.assertEqual(response.json()['type'], self.disk_data['type'])

    @parameterized.expand([
        ('exists_disk', 200),
        ('non_exists_disk', 404), 
        ('invalid_disk_size', 400)
    ])
    def test03_resize_disk(self, case, response_code):
        """ OVC-001
        #. Create Account (A1), should succeed.
        #. Create disk (D1), should succeed.
        #. List account (A1) disks, (D1) should be listed. 
        """
        diskId = self.diskId
        size = self.disk_data['size'] + random.randint(1, 20)
        
        if case == 'non_exists_disk':
            diskId = random.randint(100000, 200000)
        elif case == 'invalid_disk_size':
            size = self.disk_data['size'] - random.randint(1, 20)

        response = self.api.cloudapi.disks.resize(diskId=diskId, size=size)
        self.assertEqual(response.status_code, response_code, response.content)

        if case == "exists_disk":
            response = self.api.cloudapi.disks.get(diskId=diskId)
            self.assertEqual(response.status_code, response_code, response.content)
            self.assertEqual(response.json()['sizeMax'], size)

    @parameterized.expand([
        ('exists_disk', 200),
        ('non_exists_disk', 404), 
        ('invalid_disk', 400)
    ])
    def test04_delete_disk(self, case, response_code):
        """ OVC-001
        #. Create Account (A1), should succeed.
        #. Create disk (D1), should succeed.
        #. Delete account (A1) disks, (D1) should be listed. 
        """
        diskId = self.diskId

        if case == 'non_exists_disk':
            diskId = random.randint(100000, 200000)
        elif case == 'invalid_disk':
            diskId = self.utils.random_string()

        response = self.api.cloudapi.disks.delete(diskId=diskId)
        self.assertEqual(response.status_code, response_code, response.content)
        


