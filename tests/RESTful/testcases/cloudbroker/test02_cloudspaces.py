from testcases import *
from nose_parameterized import parameterized
import random , unittest, time 

class permission(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.admin_user = self.whoami
        
        self.log.info("Create user[U2] with user group. ")
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.user= user_data["username"]
        self.CLEANUP['users'].append(user_data["username"])
        self.user_api.system.usermanager.authenticate(user_data["username"], user_data["password"])
        
        self.log.info("[*] Create account ")
        self.account, response = self.api.cloudbroker.account.create(self.user)
        self.assertEqual(response.status_code, 200)
        self.accountId = response.json()
        self.CLEANUP["accounts"].append(self.accountId)

        self.log.info(" [*] Create cloudspace.")
        self.cloudspace, response = self.api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,
                                                access=self.user)
        self.assertEqual(response.status_code, 200)       
        self.cloudspaceId = response.json()
        self.assertEqual(self.api.wait_for_cloudspace_status(self.cloudspaceId ),"DEPLOYED")

    @parameterized.expand([('user', 403), ('admin', 200)])
    def test001_adduser_with_diff_users_access(self, access , return_code):
        """ OVC-000
        *Test case for adding user to cloudspace with [admin, user] user.*

        **Test Scenario:**
        #. Create user[U2] with user group.
        #. Create user[U3] with user group . 
        #. Add user to the cloudspace with admin user , should succeed.
        #  Add user to the cloudspace with user with user group . should fail. 
        """
        
        self.log.info(" Create user[U3] with user group.")
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.CLEANUP['users'].append(user_data["username"])


        api = self.api if access == "admin" else self.user_api 
 
        self.log.info("Add user to the cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        accesstype= random.choice(['R','RCX' ,'ARCXDU'])
        data, response = api.cloudbroker.cloudspace.addUser(username=user_data["username"], cloudspaceId=self.cloudspaceId,accesstype=accesstype)
        self.assertEqual(response.status_code, return_code)       

    @parameterized.expand([('user', 403), ('admin', 200)])
    def test002_delete_user_with_diff_users_access(self,access, return_code):
        """ OVC-000
        *Test case for testing delete user from cloudspace with [admin, user] user .*

        **Test Scenario:**
        #. Create user[U2] with user group.
        #. Delete user[U1] from  the cloudspace with admin user , should succeed.
        #  Delete user[U1] from  the cloudspace with user with user group . should fail. 
        """
        api = self.api if access == "admin" else self.user_api 

        self.log.info("delete user from the cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.deleteUser(cloudspaceId=self.cloudspaceId,username=self.user)
        self.assertEqual(response.status_code, return_code)  

    @parameterized.expand([('user', 403), ('admin', 200)])
    def test003_create_cloudspace_with_diff_users_access(self, access, return_code):
        """ OVC-000
        *Test case for testing creating cloudspace with different users with [admin, user] user.*

        **Test Scenario:*
        #. Create cloudspace[CS] with admin user, should succeed.
        #. Create cloudspace[CS] with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("Create cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        data, response = api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,
                                                access=self.user)
        self.assertEqual(response.status_code, return_code)         

    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test004_destroy_cloudspace_with_different_users_access(self, access, return_code):
        """ OVC-000
        *Test case for testing destroy  cloudspace with different users with [admin, user] user .*

        **Test Scenario:*
        #. Destroy cloudspace[CS] with admin user, should succeed.
        #. Destroy cloudspace[CS] with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("Destroy cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.destroy(accountId=self.accountId, cloudspaceId= self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)         

    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test005_start_stop_fireWall(self, access, return_code):
        """ OVC-000
        *Test case  for testing enable and disable virtual firewall with [admin, user] user *

        **Test Scenario:**

        #. create a cloud space
        #. deploy,stop and start fire wall in cloudspace with admin user, should succeed. 
        #. deploy,stop and start fire wall in cloudspace with user group, should fail.

        """
        api = self.api if access == "admin" else self.user_api 

        self.log.info("Deploy VFW with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.deployVFW(self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)

        self.log.info("Stop VFW with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.startVFW(self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)

        self.log.info("Start VFW with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.stopVFW(self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)   

    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test006_destroy_cloudspaces(self, access, return_code):
        """ OVC-00
        *Test case for deleting multiple cloudspaces with [admin, user] user .*

        **Test Scenario:**

        #. Create cloudspaces [CS1] and [CS2],  should succeed .
        #. Destroy cloudspaces[CS1] and [CS2] with user with user group, should fail.
        #. Destroy cloudspaces[CS1] and [CS2] with admin user, should succeed.

        """
        api = self.api if access == "admin" else self.user_api 

        self.log.info(" Destroy  cloudspaces with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        cloudspaces = [self.cloudspaceId]
        data,response=self.api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,
                                                access=self.user)
        self.assertEqual(response.status_code, 200)
        cloudspaces.append(response.json())
        
        self.log.info(" Delete cloudspaces [CS1], [CS2], should fail.")
        response= api.cloudbroker.cloudspace.destroyCloudSpaces([cloudspaces[1],cloudspaces[0]])
        self.assertEqual(response.status_code, return_code)


    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test007_destroy_VFW_with_different_users_access(self, access, return_code):
        """ OVC-000
        *Test case for testing destroy  VFW with different users with [admin, user] user .*

        **Test Scenario:*
        #. Destroy VFW with admin user, should succeed.
        #. Destroy VFW with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("Destroy cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.destroyVFW(cloudspaceId= self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)     

    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test008_get_VFW_with_different_users_access(self, access, return_code):
        """ OVC-000
        *Test case for testing get VFW with different users .*

        **Test Scenario:*
        #. Get VFW with admin user, should succeed.
        #. Get VFW with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("Destroy cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.getVFW(cloudspaceId= self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)     


    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test009_update_cloudspace_with_different_users_access(self, access, return_code):
        """ OVC-000
        *Test case for testing update  cloudspace with different users with [admin, user] user .*

        **Test Scenario:*
        #. Get VFW with admin user, should succeed.
        #. Get VFW with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("Destroy cloudspace with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        data, response = api.cloudbroker.cloudspace.update(cloudspaceId= self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)     


    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test010_moveVirtualFirewallToFirewallNode(self, access, return_code):
        """ OVC-000
        *Test case for testing update  cloudspace with different users with [admin, user] user .*

        **Test Scenario:*
        #. Try to moveVirtualFirewallToFirewallNode  with admin user, should succeed.
        #. Get moveVirtualFirewallToFirewallNode  with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        reouteros_nid= self.api.cloudbroker.cloudspace.getVFW(self.cloudspaceId).json()["nid"]
        targetNid = self.api.get_running_nodeId(reouteros_nid)      
        self.log.info("MoveVirtualFirewallToFirewallNode with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.moveVirtualFirewallToFirewallNode(self.cloudspaceId, targetNid)
        self.assertEqual(response.status_code, return_code)   


    @parameterized.expand([('user', 403), ('admin', 200)])  
    def test011_update_cloudspace(self, access, return_code):
        """ OVC-000
        *Test case for testing update  cloudspace with different users with [admin, user] user .*

        **Test Scenario:*
        #. Try to moveVirtualFirewallToFirewallNode  with admin user, should succeed.
        #. Get moveVirtualFirewallToFirewallNode  with user with user group, should fail.

        """

        api = self.api if access == "admin" else self.user_api 

        self.log.info("update with %s level user, should %s  "%(access, "succeed" if access== "admin" else "fail" ))
        response = api.cloudbroker.cloudspace.update(self.cloudspaceId)
        self.assertEqual(response.status_code, return_code)   

class operations(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.user = self.whoami
        self.log.info("[*] Create account ")
        self.account, response = self.api.cloudbroker.account.create(username=self.user)
        self.assertEqual(response.status_code, 200)
        self.accountId = response.json()
        self.CLEANUP["accounts"].append(self.accountId)


        self.log.info(" [*] Create cloudspace.")
        self.cloudspace, response = self.api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,
                                                access=self.user)
        self.assertEqual(response.status_code, 200)       
        self.cloudspaceId = response.json()
        self.assertEqual(self.api.wait_for_cloudspace_status(self.cloudspaceId ),"DEPLOYED")

    @parameterized.expand(['deleted','non-exist'])  
    def test001_add_nonexistuser_to_cloudspace(self, status):
        """ OVC-000
        *Test case for adding non-exist user to cloudspace .*

        **Test Scenario:**
        #. Add non-exist user to cloudspace [CS1], should fail. 
        #. Create user [U1] then delete him . 
        #. Add deleted user[ U1] to cloudspace [CS1], should fail . 
        """

        user = self.utils.random_string()
        if status == "deleted":
            self.log.info("Deleted user [U1] ")
            response = self.api.cloudbroker.user.delete(self.user)
            self.assertEqual(response.status_code, 200)
            user =self.user

        self.log.info("Add %s user to cloudspace [CS1], should fail. "%status)
        data, response = self.api.cloudbroker.cloudspace.addUser(username=user, cloudspaceId=self.cloudspaceId,accesstype="R")
        self.assertEqual(response.status_code, 404) 
  
    @parameterized.expand([('R',200,403,403),
                           ('RCX',200,403,200),
                            ('ARCXDU',200,200,200)
                            ])
    @unittest.skip("https://github.com/0-complexity/openvcloud/issues/1436")
    def test002_add_user_to_cloudspace(self,accesstype,get_code,update_code, vm_code):
        """ OVC-000
        *Test case for adding user to cloudspace with different accesstypes.*

        **Test Scenario:**
   
        #. Create user [u1].
        #. Create cloudspace[CS1] for main user and get this cloudspace  with main user,should succeed.
        #. Try to get cloudspace[CS1] with user[U1], should fail. 
        #. Add user[U1] to [CS1] with access[accesstype], should succeed.
        #. If accesstype read [R], should succeed to get cloudspace[CS1] with user[U1]
                                 , should fail to update or create  VM on it .
        #. If accesstype write [RCX], should succeed to get cloudspace[CS1] and create VM on it .
                                    , should fail to update cloudspace[CS1] name. 
        #. If accesstype admin [ARCXDU], should succeed to get , update [CS1] name and  create VM  on it. 

        """

        self.log.info("Create user [u1].")
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.CLEANUP['users'].append(user_data["username"])

        self.log.info("Create cloudspace[CS1] for main user and get this cloudspace  with main user,should succeed.")
        response= self.api.cloudapi.cloudspaces.get(self.cloudspaceId)
        self.assertEqual(response.status_code,200)

        self.log.info("Try to get cloudspace[CS1] with user[U1], should fail.")
        self.user_api.system.usermanager.authenticate(user_data["username"], user_data["password"])
        response= self.user_api.cloudapi.cloudspaces.get(self.cloudspaceId)
        self.assertEqual(response.status_code,403)       

        self.log.info("Add user[U1] to [CS1] with access[%s], should succeed."%accesstype)
        data, response = self.api.cloudbroker.cloudspace.addUser(username=user_data["username"], cloudspaceId=self.cloudspaceId,accesstype=accesstype)
        self.assertEqual(response.status_code, 200)

        self.log.info("Check that user get the right % access on cs "%accesstype)
        response=self.user_api.cloudapi.cloudspaces.get(self.cloudspaceId)
        self.assertEqual(response.status_code,get_code)
        data,response = self.user_api.cloudapi.machines.create(self.cloudspaceId)
        self.assertEqual(response.status_code,vm_code)

        data,response=self.user_api.cloudapi.cloudspaces.update(cloudspaceId=self.cloudspaceId)
        self.assertEqual(response.status_code, update_code)


    @parameterized.expand([('non-exist',404),
                           ('exist',200),
                           ('deleted',404)
                            ])
    def test003_start_stop_fireWall(self, value, return_code):
        """ OVC-000
        *Test case  for testing enable and disable virtual firewall*

        **Test Scenario:**

        #. create a cloud space
        #. deploy,stop and start fire wall in exist cloudspace, should succeed. 
        #. deploy,stop and start fire wall in none-exist cloudspace, should fail.
        """
        if value == "non-exist":
            cloudspaceId = random.randint(2000,3000)
        elif value == "deleted":
            response = self.api.cloudbroker.cloudspace.destroy(self.accountId, self.cloudspaceId)            
            cloudspaceId = self.cloudspaceId
        else:
            cloudspaceId = self.cloudspaceId


        self.log.info ("Deploy VFW to %s cloudspace , should %s"%(value, "fail" if value != "exist" else "succeed"))
        response = self.api.cloudbroker.cloudspace.deployVFW(cloudspaceId)
        self.assertEqual(response.status_code, return_code)

        self.log.info("Stop VFW to %s cloudspace , should %s"%(value, "fail" if value != "exist" else "succeed"))
        response = self.api.cloudbroker.cloudspace.startVFW(cloudspaceId)
        self.assertEqual(response.status_code, return_code)

        self.log.info("Start the virtual fire wall, should succeed.")
        response = self.api.cloudbroker.cloudspace.stopVFW(cloudspaceId)
        self.assertEqual(response.status_code, return_code)       

    @parameterized.expand([("Negative values", -1, 400),
                           ("Positive values", 1, 200)])    
    def test004_create_cloudspace_with_different_options(self, type, factor, return_code):
        """ OVC-000
        *Test case for testing creating cloudspace with different options .*

        **Test Scenario:**

        #. Create account with passing negative values in the account's limitation, should fail.
        #. Create account with certain limits, should succeed.
        """

        self.log.info("Create account with passing %s values in the cloudspace's limitation." % type)
        cloudspace_limitation = {"maxMemoryCapacity": random.randint(2, 1000) * factor,
                               "maxVDiskCapacity": random.randint(2, 1000) * factor,
                               "maxCPUCapacity": random.randint(2, 1000) * factor,
                               "maxNetworkPeerTransfer": random.randint(2, 1000) * factor,
                               "maxNumPublicIP": random.randint(2, 1000) * factor}
        data, response = self.api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,access=self.user, **cloudspace_limitation)
        self.assertEqual(response.status_code, return_code, "A resource limit should be a positive number or -1 (unlimited).")


    @unittest.skip("https://github.com/0-complexity/openvcloud/issues/1435")
    def test005_create_cloudspace_with_limitations(self):
        """ OVC-000
        *Test case for testing creating cloudspace wuth different limitations .*

        **Test Scenario:**

        #. Create account[C1] with certain limits and max_IPs equal 1, should succeed.
        #. Create cloudspace [CS2] that exceeds one of account limitations , should fail.
        #. Create cloudspace [CS3] that doesn't exceed account's limits, should succeed.
        #. Create another cloudspace [CS4] that doesn't exceed account's limits , should fail as max_IPs equal 1.
        
        """
        self.log.info("Create account[C1] with certain limits and max_IPs equal 1, should succeed.")
        account_limitation = {"maxMemoryCapacity": random.randint(2, 1000) ,
                               "maxVDiskCapacity": random.randint(2, 1000) ,
                               "maxNetworkPeerTransfer": random.randint(2, 1000) ,
                               "maxNumPublicIP": 1}        
        data, account = self.api.cloudbroker.account.create(username=self.user, **account_limitation)
        self.assertEqual(account.status_code, 200)
        self.CLEANUP['accounts'].append(account.json())

        self.log.info("Create cloudspace [CS2] that exceeds one of account limitations , should fail")
        cloudspacelimit = random.choice(list(account_limitation))
        cloudspace_limitation = {cloudspacelimit: account_limitation[cloudspacelimit]+1}
        data, response = self.api.cloudbroker.cloudspace.create(accountId=account.json(), location=self.location,access=self.user, **cloudspace_limitation)
        self.assertEqual(response.status_code, 400)

        self.log.info(" Create cloudspace [CS3] that doesn't exceed account's limits, should succeed. ")
        data, response = self.api.cloudbroker.cloudspace.create(accountId=account.json(), location=self.location,access=self.user)
        self.assertEqual(response.status_code, 200)

        self.log.info("Create another cloudspace [CS4] that doesn't exceed account's limits , should fail as max_IPs equal 1.")
        data, response = self.api.cloudbroker.cloudspace.create(accountId=account.json(), location=self.location,access=self.user)

        self.assertEqual(response.status_code, 200)       


    @parameterized.expand([("exist", 200),
                           ("Non-exist", 404)])    
    def test006_destroy_cloudspace(self,status, return_code):
        """ovc-000
        *Test case for testing destroy exist and non-exist cloudspace .*
        
        **Test Scenario:**

        #. Destroy cloudspace[CS1], should succeed.
        #. Check that cloudspace destroyed sucessfully.

        """
        if status == "exist" :
            cloudspaceId = self.cloudspaceId
        else :
            cloudspaceId = random.randint(2000,3000)

        self.log.info("Destroy  %s cloudspace, should %s"%( status, "succeed"if status== "exist" else "fail"))
        response = self.api.cloudbroker.cloudspace.destroy(self.accountId, cloudspaceId)
        self.assertEqual(response.status_code, return_code)
        
        if status == "exist":
            self.log.info("Check that cloudspace destroyed successfully. ")
            response = self.api.cloudapi.cloudspaces.get(cloudspaceId)
            self.assertEqual(response["status"], "DESTROYED")

            self.log.info("Try to destroy cloudspace [CS1] again, should fail ")
            response = self.api.cloudbroker.cloudspace.destroy(self.accountId, cloudspaceId)
            self.assertEqual(response.status_code, 404)            

    def test007_destroy_cloudspaces(self):
        """ OVC-000
        *Test case for deleting multiple account.*

        **Test Scenario:**

        #. Create cloudspaces [CS1],[CS2] , [CS3] and [CS4], should succeed .
        #. Delete cloudspace [CS1], should succeed.
        #. Delete cloudspaces [CS1], [CS2], should fail.
        #. Delete [CS2] and [CS3] cloudspaces using destroy cloudspaces  api, should succeed. 
        #. Check that the four cloudspaces deleted ,should succeed.
        """
        self.log.info(" Create cloudspaces [CS1],[CS2] , [CS3] and [CS4], should succeed .")
        cloudspaces = [self.cloudspaceId]
        for _ in range(3):
            data,response=self.api.cloudbroker.cloudspace.create(self.accountId, self.location, self.user)
            self.assertEqual(response.status_code, 200)
            cloudspaces.append(response.json())

        self.log.info("Delete cloudspace [CS1], should succeed.")
        response= self.api.cloudbroker.cloudspace.destroy(self.accountId, cloudspaces[0])
        self.assertEqual(response.status_code, 200)
        
        self.log.info(" Delete cloudspaces [CS1], [CS2], should fail.")
        response= self.api.cloudbroker.cloudspace.destroyCloudSpaces([cloudspaces[1],cloudspaces[0]])
        self.assertEqual(response.status_code, 404)

        self.log.info("Delete [CS2] and [CS3] cloudspaces using destroy cloudspaces  api, should succeed. ")
        response= self.api.cloudbroker.cloudspace.destroyCloudSpaces([cloudspaces[2],cloudspaces[3]])
        self.assertEqual(response.status_code, 200)

        self.log.info("Check that the four cloudspaces deleted ,should succeed.")
        for cloudspaceId in cloudspaces:
            response = self.api.cloudapi.cloudspaces.get(cloudspaceId)
            self.assertEqual(response.json()["status"],"DESTROYED")

    @parameterized.expand([("exist", 200),
                           ("Non-exist", 404)])   
    def test008_destroy_VFW(self, status, return_code):
        """ OVC-000
        *Test case for destroy vfw for non-exist and exist cloudspace .*

        **Test Scenario:**

        #. Create cloudspaces [CS1].
        #. Destroy VFW for non-exist cloudspace, should fail.
        #. Destroy VFW of this cloudspace, should succeed.
        #. Check that VFW of cloudspace destroyed , should succeed. 
        """
        if status == "exist" :
            cloudspaceId = self.cloudspaceId
        else :
            cloudspaceId = random.randint(2000,3000)

        self.log.info(" Destroy VFW of this cloudspace, should succeed.")
        response = self.api.cloudbroker.cloudspace.destroyVFW(cloudspaceId)
        self.assertEqual(response.status_code, return_code)

        if status == "exist":
            self.log.info(" Check that VFW of cloudspace destroyed , should succeed. ")
            response = self.api.cloudapi.cloudspaces.get(cloudspaceId)
            self.assertEqual(response.json()["status"], "VIRTUAL")


    def test009_delete_non_exist_user_from_cloudspace(self):
        """ OVC-000
        *Test case for deleting non-exist user from cloudspace. *

        **Test Scenario:**
        #. Create cloudspace [CS1].
        #. Delete non-exist user from [CS1], should fail.
        """
        fake_user=self.utils.random_string()
        response = self.api.cloudbroker.cloudspace.deleteUser(cloudspaceId=self.cloudspaceId, username=fake_user)
        self.assertEqual(response.status_code, 404)


    def test010_delete_user_from_cloudspace(self):
        """ OVC-000
        *Test case for deleting user from cloudspace. *

        **Test Scenario:**
        #. Create user[U1] .
        #. Create cloudspace [CS1]
        #. Delete non-exist user from [CS1], should fail.
        #. Add user[U1] to cloudspace[CS1], should succeed.
        #. Delete user[U1] from [CS1], should succeed.
        #. Delete user[U1] again from [CS1], should fail .
        
        """
        self.log.info("Create user [u1].")
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.CLEANUP['users'].append(user_data["username"])
 
        self.log.info("Add user[U1] to [CS1] , should succeed")
        data, response = self.api.cloudbroker.cloudspace.addUser(username=user_data["username"], cloudspaceId=self.cloudspaceId,accesstype='R')
        self.assertEqual(response.status_code, 200)

        self.log.info(" Delete non-exist user from [CS1], should fail. ")
        fake_user= self.utils.random_string()
        response = self.user_api.cloudbroker.cloudspace.deleteUser(cloudspaceId=self.cloudspaceId, username=fake_user)
        self.assertEqual(response.status_code, 404)        

        self.log.info("Delete user[U1] from [CS1], should succeed.")
        response = self.api.cloudbroker.cloudspace.deleteUser(cloudspaceId=self.cloudspaceId, username=self.user)
        self.assertEqual(response.status_code, 200)

        self.log.info("Delete  user[U1]  again from [CS1], should fail .")
 
        response = self.api.cloudbroker.cloudspace.deleteUser(cloudspaceId=self.cloudspaceId, username=self.user)
        self.assertEqual(response.status_code, 404)

    def test011_create_cloudspace_with_nonexist_user(self):
        """ OVC-000
        *Test case for testing creating account wuth different options .*

        **Test Scenario:*
        #. Create cloudspace[CS] with non-exist user, should fail.
        """
        fake_user = self.utils.random_string()
        data, response = self.api.cloudbroker.cloudspace.create(accountId=self.accountId, location=self.location,
                                                access=fake_user)
        self.assertEqual(response.status_code, 404) 


    @parameterized.expand([("non-exist-cloudspace", 404),
                           ("Non-exist-node", 404),
                           ("deleted-cloudspace",404),
                           ("exist-cloudspace&node",200)])   
    def test008_moveVirtualFirewallToFirewallNode(self, status, return_code):
        """ OVC-000
        *Test case for destroy vfw for non-exist and exist cloudspace .*

        **Test Scenario:**

        #. Create cloudspaces [CS1].
        #. Get random target node .
        #. Try to moveVirtualFirewall of deleted  cloudspace To FirewallNode, should fail.
        #. Try to moveVirtualFirewall of non-exist cloudspace To FirewallNode, should fail.
        #. Try to moveVirtualFirewall To non-exist Node, should fail .
        #. Try to moveVirtualFirewall of exist cloudspace To FirewallNode, should succeed .
        #. Check that firewall moved successfully.
        """
        routeros_nid= self.api.cloudbroker.cloudspace.getVFW(self.cloudspaceId).json()["nid"]
        targetNid = self.api.get_running_nodeId(routeros_nid)      
        cloudspaceId = self.cloudspaceId

        if status == "Non-exist-node" :
            self.skipTest("https://github.com/0-complexity/openvcloud/issues/1447")
            targetNid= random.randint(100,200)

        elif status == "non-exist-cloudspace":
            cloudspaceId = random.randint(2000,3000)
        elif status == "deleted-cloudspace":
            self.skipTest("https://github.com/0-complexity/openvcloud/issues/1439")
            response = self.api.cloudbroker.cloudspace.destroy(self.accountId, self.cloudspaceId)            

        self.log.info("MoveVirtualFirewallToFirewallNode with %s , should %s  "%(status, "succeed" if status == "exist-cloudspace" else "fail" ))
        response = self.api.cloudbroker.cloudspace.moveVirtualFirewallToFirewallNode(cloudspaceId, targetNid)
        self.assertEqual(response.status_code, return_code)   

        if status =="exist-cloudspace&node":
            self.log.info("Check that firewall moved successfully.")
            new_nid= self.api.cloudbroker.cloudspace.getVFW(self.cloudspaceId).json()["nid"]
            self.assertEqual(new_nid, targetNid)
            

    @parameterized.expand([("non-exist", 404),
                           ("deleted", 404),
                           ("exist",200)])   
    def test009_update_cloudspace(self, status, return_code):
        """ OVC-000
        *Test case for update non-exist and exist cloudspace .*

        **Test Scenario:**

        #. Create cloudspaces [CS1].
        #. Update non-exist cloudspace name , should fail. 
        #. Update Deleted cloudspace name , should fail . 
        #. Update exist cloudspace name , should succeed.
        #. Check that cloudspace name updated successfully.
    
        """

        cloudspaceId = self.cloudspaceId
        if status == "non-exist":
            cloudspaceId = random.randint(3000,5000) 
        elif status == "deleted":
            self.skipTest("https://github.com/0-complexity/openvcloud/issues/1439")
            response = self.api.cloudbroker.cloudspace.destroy(self.accountId, self.cloudspaceId) 
        
        data, response= self.api.cloudbroker.cloudspace.update(cloudspaceId)
        self.assertEqual(response.status_code, return_code)       

        if status == "exist":
            response = self.api.cloudapi.cloudspaces.get(cloudspaceId)
            self.assertEqual(data["name"], response.json()["name"])