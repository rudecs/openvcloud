import random, time, unittest
from testcases import *
from nose_parameterized import parameterized
from framework.api.client import Client

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
    
    @parameterized.expand([('admin', 200), ('user', 403)])
    def test01_get_account(self, role, status_code):
        """ OVC-001
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to get account (A1)'s info using user (U2), should succeed.
        #. Try to get account (A1)'s info using user (U3), should fail.
        """
        self.log.info('Try to get account (A1)\'s info using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.get(accountId=self.account_id)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test02_update_account(self, role, status_code):
        """ OVC-002
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to update account (A1)'s info using user (U2), should succeed.
        #. Try to update account (A1)'s info using user (U3), should fail.
        """
        self.log.info('Try to update account (A1)\'s info using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.update(accountId=self.account_id)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test03_add_user(self, role, status_code):
        """ OVC-003
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Create user (U4), should succeed.
        #. Try to add user (U4) to account (A1) using user (U2), should succeed.
        #. Try to add user (U4) to account (A1) using user (U3), should fail.
        """
        self.log.info('Create user (U4), should succeed')
        userId, userPassword = self.api.create_user()
        self.CLEANUP['users'].append(userId)

        self.log.info('Try to add user (U4) to account (A1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.addUser(accountId=self.account_id, userId=userId)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test04_update_user(self, role, status_code):
        """ OVC-004
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Create user (U4), should succeed.
        #. Add user (U4) to account (A1), should succeed.
        #. Try to update user (U4) access of account (A1) using user (U2), should succeed.
        #. Try to update user (U4) access of account (A1) using user (U3), should fail.
        """
        self.log.info('Create user (U4), should succeed')
        userId, userPassword = self.api.create_user()
        self.CLEANUP['users'].append(userId)

        self.log.info('Add user (U4) to account (A1), should succeed')
        self.api.cloudapi.accounts.addUser(accountId=self.account_id, userId=userId)
        
        self.log.info('Try to update user (U4) access of account (A1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        data, response = api.cloudapi.accounts.updateUser(accountId=self.account_id, userId=userId)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test05_delete_user(self, role, status_code):
        """ OVC-005
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Create user (U4), should succeed.
        #. Add user (U4) to account (A1), should succeed.
        #. Try to delete user (U4) from account (A1) using user (U2), should succeed.
        #. Try to delete user (U4) from account (A1) using user (U3), should fail.
        """
        self.log.info('Create user (U4), should succeed')
        userId, userPassword = self.api.create_user()
        self.CLEANUP['users'].append(userId)

        self.log.info('Add user (U4) to account (A1), should succeed')
        self.api.cloudapi.accounts.addUser(accountId=self.account_id, userId=userId)
        
        self.log.info('Try to delete user (U4) from account (A1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.deleteUser(accountId=self.account_id, userId=userId)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test06_get_consumed_cloud_units(self, role, status_code):
        """ OVC-006
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to get consumed cloud units of account (A1) using user (U2), should succeed.
        #. Try to get consumed cloud units of account (A1) using user (U3), should fail.
        """
        self.log.info('Try to get consumed cloud units of account (A1) using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.getConsumedCloudUnits(accountId=self.account_id)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    @unittest.skip('https://github.com/0-complexity/openvcloud/issues/1154')
    def test07_get_consumed_cloud_units_by_type(self, role, status_code):
        """ OVC-007
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to get consumed cloud units of account (A1) by type using user (U2), should succeed.
        #. Try to get consumed cloud units of account (A1) by type using user (U3), should fail.
        """   
        self.log.info('Try to get consumed cloud units of account (A1) by type using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )    
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.getConsumedCloudUnitsByType(accountId=self.account_id)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test08_get_consumption(self, role, status_code):
        """ OVC-008
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to get consumption of account (A1) by type using user (U2), should succeed.
        #. Try to get consumption of account (A1) by type using user (U3), should fail.   
        """   
        now = time.time()
        delta = 60 * 60 * 3
        start = now - delta        
        end = now + delta
        
        self.log.info('Try to get consumption of account (A1) by type using user %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )

        api = self.admin_api if role == 'admin' else self.user_api
        api.api_client.load_swagger()

        response = api.cloudapi.accounts.getConsumption(accountId=self.account_id, start=start, end=end)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    @unittest.skip('https://github.com/0-complexity/openvcloud/issues/1333')
    def test09_create_account(self, role, status_code):
        """ OVC-009
        #. Create users (U1) with admin access.
        #. Create users (U2) with user access.
        #. Try to create account (A1) using user (U1), should succeed.
        #. Try to create account (A1) using user (U2), should fail. 
        """
        access = self.admin if role == 'admin' else self.user
        api = self.admin_api if role == 'admin' else self.user_api
        data, response = api.cloudapi.accounts.create(access=access)
        self.assertEqual(response.status_code, status_code, response.content)

    @parameterized.expand([('admin', 200), ('user', 403)])
    def test10_list_templates(self, role, status_code):
        """ OVC-010
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. Try to list account (A1)'s templates using user (U2), should succeed.
        #. Try to list account (A1)'s templates using user (U3), should fail.
        """
        self.log.info('Try to list account (A1)\'s templates using %s, should %s' % 
            (('(U2)', 'succeed') if role == 'admin' else ('(U3)', 'fail'))
        )
        api = self.admin_api if role == 'admin' else self.user_api
        response = api.cloudapi.accounts.listTemplates(accountId=self.account_id)
        self.assertEqual(response.status_code, status_code, response.content)

    def test11_list_accounts(self):
        """ OVC-011
        #. Create users (U1) with admin access.
        #. Create users (U2) with admin access.
        #. Create users (U3) with user access.
        #. Create Account (A1) using user (U1).
        #. List user (U1)'s accounts, account (A1) should be listed.
        #. List user (U2)'s accounts, account (A1) shouldn't be listed.
        #. List user (U3)'s accounts, account (A1) shouldn't be listed.
        """
        self.log.info('List user (U1)\'s accounts, account (A1) should be listed')
        response = self.api.cloudapi.accounts.list()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn(self.account_id, [x['id'] for x in response.json()])

        self.log.info('List user (U2)\'s accounts, account (A1) shouldn\'t be listed')        
        response = self.admin_api.cloudapi.accounts.list()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(response.json())

        self.log.info('List user (U3)\'s accounts, account (A1) shouldn\'t be listed')                
        response = self.user_api.cloudapi.accounts.list()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(response.json())
