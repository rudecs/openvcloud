import unittest
from ....utils.utils import BasicACLTest
import uuid
import random
from JumpScale.baselib.http_client.HttpClient import HTTPError
import email
import imaplib
import mailbox
import json

class UsersBasicTests(BasicACLTest):

    def setUp(self):
        super(UsersBasicTests, self).setUp()
        self.acl_setup(create_default_cloudspace=False)

    def test001_authenticate_user(self):
        """ OVC-031
        * Test case for check user authentication and passsword update. *

        **Test Scenario:**

        #. Create user (U1) with admin access.
        #. Authenticate U1,should return session key[user1_key] .
        #. Use U1's key to list the accounts for U1, should succeed.
        """
        self.lg('%s STARTED' % self._testID)

        self.lg('- Create user1 with admin access ')
        old_password = str(uuid.uuid4()).replace('-', '')[0:10]
        user1 = self.cloudbroker_user_create(group='admin', password=old_password)

        self.lg("- Authenticate U1 ,should return session key[user1_key] .")
        user1_key = self.get_authenticated_user_api(username=user1, password=old_password)
        self.assertTrue(user1_key)

        self.lg("-  Use U1's key to list the accounts for U1, should succeed.")
        accounts_list = user1_key.cloudapi.accounts.list()
        self.assertEqual(accounts_list, [])

    def test002_get_user_info(self):
        """ OVC-032
        * Test case for check get user information.*

        **Test Scenario:**

        #. Create user (U1) with admin access and Email.
        #. Get U1 info with /cloudapi/users/get Api, should succeed.
        #. Check that U1's info is right, should succeed.
        #. Set data for U1 with /cloudapi/users/setData API, Should succeed.
        #. Check that this data has been added to U1 info ,should succeed.

        """
        self.lg('%s STARTED' % self._testID)
        self.lg('- Create user (U1) with admin access and Email ')
        user1 = self.cloudbroker_user_create(group='admin')
        user1_email = "%s@example.com"%user1

        self.lg("- Authenticate U1 ,sould succeed .")
        user1_key = self.get_authenticated_user_api(user1)
        self.assertTrue(user1_key)

        self.lg("- Get U1 info with /cloudapi/users/get Api, should succeed")
        response = user1_key.cloudapi.users.get(username=user1)
        self.assertIn(user1_email, response["emailaddresses"])

        self.lg("- Set data for U1 with /cloudapi/users/setData API, Should succeed.")
        data = {"key":"value"}
        response = user1_key.cloudapi.users.setData(data=json.dumps(data))
        self.assertTrue(response)

        self.lg(' Check that this data has been added to U1 info ,should succeed.')
        response = user1_key.cloudapi.users.get(username=user1)
        self.assertDictEqual(data, response["data"])

    def test003_check_matching_users(self):
        """ OVC-033
        * Test case for check get matching usernames.

        **Test Scenario:**

        #. Create user1 with random name user1.
        #. Create user2 with name in which user1 name is part of it .
        #. Use user1 name to get matching usernames with /cloudapi/users/getMatchingUsernames Api,sould succeed.
        #. Check that userr1 ,user2   in matching list, should succeed.
        #. Delete user1 and user2 and make sure that they can't be listed.
        """
        self.lg('%s STARTED' % self._testID)

        self.lg('- Create user1 with random name . ')
        user1_name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.cloudbroker_user_create(username=user1_name)

        self.lg("- Authenticate U1 ,sould succeed .")
        user1_key = self.get_authenticated_user_api(user1_name)
        self.assertTrue(user1_key)

        self.lg("- Create user2 with name in which user1 name is part of it")
        user2_name = "match%s"%user1_name
        self.cloudbroker_user_create(username=user2_name)

        self.lg("- Use user1 name to get matching usernames with /cloudapi/users/getMatchingUsernames Api,sould succeed.")
        limit = random.randint(3, 20)
        matching_users_names = self.api.cloudapi.users.getMatchingUsernames(usernameregex=user1_name, limit=limit)

        self.lg("- Check that user2 and user1  in matching list, should succeed.")
        self.assertTrue([x for x in matching_users_names if x["username"]==user2_name ])
        self.assertTrue([x for x in matching_users_names if x["username"]==user1_name ])

        self.lg("- Delete user1 and user2 and make sure that they can't be listed.")
        self.api.cloudbroker.user.delete(username=user1_name)
        self.api.cloudbroker.user.delete(username=user2_name)

        self.CLEANUP['username'].remove(user1_name)
        self.CLEANUP['username'].remove(user2_name)

        matching_users_names = self.api.cloudapi.users.getMatchingUsernames(usernameregex = user2_name)
        self.assertFalse([x for x in matching_users_names if x["username"]==user2_name ])
        self.assertFalse([x for x in matching_users_names if x["username"]==user1_name ])

    def test005_create_users_with_same_specs(self):
        """ OVC-034
        * Test case for check creation of more than one user with same specs .

        **Test Scenario:**

        #. Create user1,sould succeed .
        #. Create User2 with same name as user1, should fail .
        #. Create User3 with same Email as User1 , should fail .

        """
        self.lg('- Create user1 with random name user1. ')
        user1_name = self.cloudbroker_user_create()
        user1_emailaddress = "%s@example.com"%user1_name

        self.lg("- Create User2 with same name as user1, should fail")
        user2_emailaddress = "%s@example.com"%(str(uuid.uuid4()).replace('-', '')[0:10])
        with self.assertRaises(HTTPError) as e:
            self.api.cloudbroker.user.create(username=user1_name, emailaddress=user2_emailaddress,
                                             password=user1_name, groups=[])
                                             
        self.lg('- expected error raised %s' % e.exception.status_code)
        self.assertEqual(e.exception.status_code, 409)

        self.lg("Create User3 with same Email as User1 , should fail . ")
        user3_name = str(uuid.uuid4()).replace('-', '')[0:10]
        with self.assertRaises(HTTPError) as e:
            self.api.cloudbroker.user.create(username=user3_name, emailaddress=user1_emailaddress,
                                             password=user3_name, groups=[])

        self.lg('- expected error raised %s' % e.exception.status_code)
        self.assertEqual(e.exception.status_code, 409)
