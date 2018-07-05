import time, random, unittest
from testcases import *
from nose_parameterized import parameterized

class UsersTests(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.data, self.response = self.api.system.usermanager.create(provider=None)
        self.assertEqual(self.response.status_code, 200, self.response.content)
        self.username = self.data['username']
        self.CLEANUP['users'].append(self.username)
    
    @parameterized.expand([('exists', 200, 'true'), ('non-exist', 404, 'false')])
    def test01_userget_userexists(self, case, response_code, userexists):
        """ OVC-001
        #. Create user (U1), should succeed.
        #. Get user (U1), should succeed.
        #. Check if user (U1) exists, should return true.
        #. Get not existing user, should fail.
        #. Check if non-existing user exists, should return false. 
        """
        if case == 'exists':
            username = self.username
        else:
            username = self.utils.random_string()

        response = self.api.system.usermanager.userget(name=username)
        self.assertEqual(response.status_code, response_code, response.content)

        response = self.api.system.usermanager.userexists(name=username)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.text, userexists)

    @parameterized.expand([('exists', 200), ('non-exist', 404)])
    def test02_edit_user(self, case, response_code):
        """ OVC-002
        #. Create user (U1), should succeed.
        #. Edit user (U1), should succeed.
        #. Edit non-existing user, should fail.
        """
        if case == 'exists':
            username = self.username
        else:
            username = self.utils.random_string()
      
        data, response = self.api.system.usermanager.editUser(username=username)
        self.assertEqual(response.status_code, response_code, response.content)

    @parameterized.expand([('exists', 200), ('non-exist', 404)])
    def test03_delete_user(self, case, response_code):
        """ OVC-003
        #. Create user (U1), should succeed.
        #. Delete user (U1), should succeed.
        #. Delete none existing user, should fail.
        """
        if case == 'exists':
            username = self.username
        else:
            username = self.utils.random_string()

        response = self.api.system.usermanager.delete(username=username)
        self.assertEqual(response.status_code, response_code, response.content)

        response = self.api.system.usermanager.userexists(name=username)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.text, 'false')

class GroupsTests(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.data, self.response = self.api.system.usermanager.createGroup()
        self.assertEqual(self.response.status_code, 200, self.response.content)
        self.name = self.data['name']

    def tearDown(self):
        self.api.system.usermanager.deleteGroup(id=self.name)
        super().tearDown()
    
    @parameterized.expand([('exists', 200), ('non-exist', 404)])
    def test01_edit_group(self, case, response_code):
        """ OVC-001
        #. Create group (G1), should succeed.
        #. Edit group (G1), should succeed.
        #. Edit non-existing group, should fail.
        """
        if case == 'exists':
            name = self.name
        else:
            name = self.utils.random_string()

        data, response = self.api.system.usermanager.editGroup(name=name)    
        self.assertEqual(response.status_code, response_code, response.content)
  
    @parameterized.expand([('exists', 200), ('non-exist', 404)])
    @unittest.skip('https://github.com/0-complexity/openvcloud/issues/1367')    
    def test02_delete_group(self, case, response_code):
        """ OVC-002
        #. Create group (G1), should succeed.
        #. Delete group (G1), should succeed.
        #. Delete non-existing group, should fail.
        """
        if case == 'exists':
            name = self.name
        else:
            name = self.utils.random_string()
       
        response = self.api.system.usermanager.deleteGroup(id=name)
        self.assertEqual(response.status_code, response_code, response.content)