#coding=utf-8
import uuid
import time
import unittest
from random import randint
from ....utils.utils import BasicACLTest
from JumpScale.portal.portal.PortalClient2 import ApiError

class ACLACCOUNT(BasicACLTest):
    def setUp(self):
        super(ACLACCOUNT, self).setUp()
        self.acl_setup(True)
        self.machine_id=self.cloudapi_create_machine(self.cloudspace_id,self.account_owner_api)

class user_group(ACLACCOUNT):
    def test001_usergroup_create_account_cloudspace(self):
        """ ACL-58
        *Test case for create user with only user group.*

        **Test Scenario:**

        #. create user1  with user group
        #. create account with user1, should return forbiden
        # .get account details,should return forbbiden
        #. create cloudspace with user1 ,should return forbbiden
        #. get cloudspace details with user1,should return forbbiden
        #. create vm  with user1 ,should return forbbiden
        #. get vm details ,should return forbidden
        #. get list of accounts should return empty list
        #. get list of cloudspaces should return empty list
        #. get list of vms should return forbidden

        """
        self.lg('%s STARTED' % self._testID)
        self.user1 = self.cloudbroker_user_create(group = 'user' )
        self.lg('1- create user %s with user domain ' % self.user1)
        self.user1_api = self.get_authenticated_user_api(self.user1)
        self.lg(' 2- create account ' )


        try:
           accountId = self.user1_api.cloudbroker.account.create(name=self.user1, username=self.user1, email='%s@gmail.com'%self.user1,
                                                        maxMemoryCapacity=-1,
                                                        maxVDiskCapacity=-1,
                                                        maxCPUCapacity=-1,
                                                        maxNumPublicIP=-1)

        except ApiError as e:
            self.lg('- expected error raised %s' % e.message)
            self.assertEqual(e.message, '403 Forbidden')

        self.lg(' 3-get account details ')

        try:
            account_details=self.user1_api.cloudapi.accounts.get(accountId=self.account_id)
            self.assertFalse(account_details)
        except ApiError as e:
            self.lg('- expected error raised %s ' %e.message)
            self.assertEqual(e.message,'403 Forbidden')


        self.lg(' 4-create cloudspace')
        try:
           cloudspaceId = self.user1_api.cloudapi.cloudspaces.create(accountId=self.account_id, location=self.location, name=self.user1,access=self.user1)
           self.assertFalse(cloudspaceId)
        except ApiError as e:
            self.lg('- expected error raised %s ' % e.message)
            self.assertEqual(e.message, '403 Forbidden')

        self.lg(' 5-get cloudspace details ')

        try:
            cloudspace_details = self.user1_api.cloudapi.cloudspaces.get(cloudspaceId=self.cloudspace_id)
            self.assertFalse(cloudspace_details)
        except ApiError as e:
            self.lg('- expected error raised %s ' % e.message)
            self.assertEqual(e.message, '403 Forbidden')

        self.lg('6-create VM')
        try:
           VM_Id = self.user1_api.cloudapi.machines.create(cloudspaceId=self.cloudspace_id, name=self.user1, sizeId=0, imageId=0, disksize=10,datadisks=[])
           self.assertFalse(VM_Id)
        except ApiError as e:
            self.lg('- expected error raised %s' % e.message)
            self.assertEqual(e.message, '403 Forbidden')

        self.lg(' 7-get vm details ')

        try:
            macine_details = self.user1_api.cloudapi.machines.get(machineId=self.machine_id)
            self.assertFalse(cloudspace_details)
        except ApiError as e:
            self.lg('- expected error raised %s ' %e.message)
            self.assertEqual(e.message,'403 Forbidden')

        self.lg(' 8- git list of accounts ' )
        accounts_list = self.user1_api.cloudapi.accounts.list()
        self.lg('acountlist %s' % accounts_list)
        self.assertEqual(accounts_list,[])
        self.lg('9-get cloudspaces lists ')
        cloudspace_list = self.user1_api.cloudapi.cloudspaces.list()
        self.lg('- cloudspace list %s ' % cloudspace_list )
        self.assertEqual(cloudspace_list,[])
        self.lg('10-get machines list' )
        try:
            machines_list = self.user1_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
            self.assertFalse(machines_list)
        except ApiError as e :
            self.lg('- expected error raised %s ' %e.message)
            self.assertEqual(e.message,'403 Forbidden')

    def test002_usergroup_add_account(self):
        """ ACL-59
        *Test case for create user with only user group.*

        **Test Scenario:**

        #. create user with user group
        #. create  account to this user should succeed
        #. create cloud space by this user from cloudbroker should be forbbiden
        #. create cloud space by this user from end user should  succeed
        #. get list of account will give list have this account
        #. get list of cloudspace give list have this cloud space
        #. update account name  from enduser with this use should succeed

        """


        self.lg('%s STARTED' % self._testID)
        self.user1 = self.cloudbroker_user_create(group = 'user' )
        self.lg('1- create user %s with user domain ' % self.user1)
        self.user1_api = self.get_authenticated_user_api(self.user1)
        self.lg(' 2- create account ')
        accountId = self.cloudbroker_account_create(name=self.user1, username=self.user1, email="%s@example.com" % self.user1)

        self.lg('creat account with Id %s' % accountId)
        self.assertTrue(accountId)
        try:
            cloudspaceId = self.user1_api.cloudbroker.cloudspace.create(accountId=self.account_id, location=self.location,name=self.user1,access=self.user1)

        except ApiError as e:
            self.lg('- expected error raised %s' % e.message)
            self.assertEqual(e.message, '403 Forbidden')

        cloudspaceId = self.cloudapi_cloudspace_create(account_id=accountId, location=self.location, access=self.user1,api=self.user1_api)
        self.assertTrue(cloudspaceId)

        self.lg('creat cloudspace  with Id %s' % cloudspaceId)
        self.lg(' 4- git list of accounts ')

        accounts_list = self.user1_api.cloudapi.accounts.list()
        self.assertEqual(len(accounts_list), 1, 'user have only one account')
        self.assertEqual(accounts_list[0]['id'], accountId)
        self.lg(' 5- git list of cloudspaces ')
        cloudspaces_list = self.user1_api.cloudapi.cloudspaces.list()
        self.assertEqual(len(cloudspaces_list), 1, 'user have only one cloudspace')
        self.assertEqual(cloudspaces_list[0]['id'], cloudspaceId)

        update_response = self.user1_api.cloudapi.accounts.update(accountId=accountId,name=self.user)
        self.assertTrue(update_response)

    def test003_usergroup_delete_user_from_account(self):
        """ ACL-60
        *Test case for create user with only user group.*

        **Test Scenario:**

        #. create user1 ,user2  with user group
        #. create account to user1
        #. try to delete user1 from this account  by himself should be bad request as user is last admin
        #. add user2 to this account by user1 should succeed
        #. delete user1 from this account by user1 should succeed
        #. create cloudspace by user2
        #. add user1 to created cloud space by user 1 should succeed
        #. try delete user1 from created cloudspace by user 1 should succeed
        #. try delete cloudspace by user1 should return forbidden
        """
        self.lg('%s STARTED' % self._testID)
        self.user1 = self.cloudbroker_user_create(group = 'user')
        self.user2 = self.cloudbroker_user_create(group = 'user')
        self.lg('1- create user1  %s  and user2 %s with user domain ' % (self.user1, self.user2))
        self.user1_api = self.get_authenticated_user_api(self.user1)
        self.user2_api = self.get_authenticated_user_api(self.user2)
        self.lg(' 2- create account ' )

        accountId = self.cloudbroker_account_create( name=self.user1,username=self.user1,email="%s@example.com" % self.user1)

        self.lg('creat account with Id %s' % accountId)
        self.assertTrue(accountId)
        self.lg('3- delete user1 from created account')
        try:
            response=self.user1_api.cloudapi.accounts.deleteUser(accountId=accountId,userId=self.user1)
        except ApiError as e :
            self.lg('-expected error raised %s' % e.message)
            self.assertEqual(e.message, '400 Bad Request')
        self.lg('4- add user2 to created account')
        response= self.user1_api.cloudapi.accounts.addUser(accountId=accountId,userId=self.user2,accesstype='ARCXDU')
        self.assertTrue(response)
        self.lg('5-delete user1 from created account after add user2')

        response=self.user1_api.cloudapi.accounts.deleteUser(accountId=accountId,userId=self.user1)
        self.assertTrue(response)

        self.lg('6-create cloudspace by user2')

        cloudspaceId = self.cloudapi_cloudspace_create(account_id=accountId, location=self.location, access=self.user2,api=self.user2_api)

        self.lg('creat cloudspace  with Id %s' % cloudspaceId)
        self.assertTrue(cloudspaceId)
        self.lg('7- add user1 to created cloudspace ')
        response = self.user2_api.cloudapi.cloudspaces.addUser(cloudspaceId=cloudspaceId,userId=self.user1,accesstype='ARCXDU')
        self.assertTrue(response)
        self.lg('8- delete user1 from created cloud space ')

        respopnse=self.user1_api.cloudapi.cloudspaces.deleteUser(cloudspaceId=cloudspaceId,userId=self.user1)
        self.assertTrue(response)
        self.lg('9- try to delete created cloud space by user 2')
        try:
            response=self.user1_api.cloudapi.cloudspaces.delete(cloudspaceId=cloudspaceId)
            self.assertFalse(response)
        except ApiError as e :
            self.lg('-expected error raised %s' % e.message)
            self.assertEqual(e.message, '403 Forbidden')


        response=self.user2_api.cloudapi.cloudspaces.delete(cloudspaceId=cloudspaceId)
        self.assertTrue(response)
