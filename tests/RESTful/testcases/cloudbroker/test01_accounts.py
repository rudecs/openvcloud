from testcases import *
from nose_parameterized import parameterized
import random, unittest



class Test(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.user=self.whoami
        self.account,self.response=self.api.cloudbroker.account.create(self.user)
        self.assertEqual(self.response.status_code, 200)
        self.CLEANUP['accounts'].append(self.response.json())

    def tearDown(self):
        super().tearDown()


    @parameterized.expand([("Negative values", -1, 400),
                           ("Positive values", 1, 200)])
    def test001_create_account_with_different_options(self, type, factor, return_code):
        """ OVC-000
        *Test case for testing creating account wuth different options .*

        **Test Scenario:**

        #. Create account with passing negative values in the account's limitation, should fail.
        #. Create account with certain limits, should succeed.
        """
        self.log.info("Create account with passing %s values in the account's limitation." % type)
        accounts_limitation = {"maxMemoryCapacity": random.randint(2, 1000) * factor,
                               "maxVDiskCapacity": random.randint(2, 1000) * factor,
                               "maxCPUCapacity": random.randint(2, 1000) * factor,
                               "maxNetworkPeerTransfer": random.randint(2, 1000) * factor,
                               "maxNumPublicIP": random.randint(2, 1000) * factor}
        data, response = self.api.cloudbroker.account.create(username=self.user, **accounts_limitation)
        self.assertEqual(response.status_code, return_code, "A resource limit should be a positive number or -1 (unlimited).")
        if return_code == 200:
            self.CLEANUP['accounts'].append(response.json())

    def test002_create_account_with_non_existing_user(self):
        """ OVC-000
        *Test case for testing creating account with non existing user.*

        **Test Scenario:**

        #. Create account with non-exist user, should fail.

        """
        self.log.info(" Create account with non-exist user, should fail.")
        fake_user = self.utils.random_string()
        data, response = self.api.cloudbroker.account.create(username=fake_user)
        self.assertEqual(response.status_code, 400, "Email address is required for new users.")

    @parameterized.expand([('R',200,403,403),
                           ('RCX',200,403,200),
                            ('ARCXDU',200,200,200)
                            ])
    def test003_add_user_to_account(self,accesstype,get_code,update_code,cloudspace_code):
        """ OVC-000
        *Test case for adding user to account with different accesstypes.*

        **Test Scenario:**
   
        #. Create user [u1].
        #. Create account[C1] for main user and get this account  with main user,should succeed.
        #. Add user[U1] to [C1]with access[accesstype], should succeed.
        #. If accesstype read [R], should succeed to get account[C1] with user[U1]
                                 , should fail to update account[C1] name or create cloudspace on it.
        #. If accesstype write [RCX], should succeed to get account[C1] and create cloudspace on it
                                    , should fail to updare account[C1] name. 
        #. If accesstype admin [ARCXDU], should succeed to get , update [C1] name and  create cloudspace on it. 
        """

        self.log.info("Create user [u1].")
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.CLEANUP['users'].append(user_data["username"])
        self.log.info("Create account[C1] for main user and get this account  with  user,should succeed.")
        response= self.api.cloudapi.accounts.get(self.response.json())
        self.assertEqual(response.status_code,200)

        self.log.info("Add user[U1] to [C1]with access[accesstype], should succeed.")
        data, response = self.api.cloudbroker.account.addUser(username=user_data["username"], accountId=self.response.json(),accesstype=accesstype)
        self.assertEqual(response.status_code, 200)

        self.user_api.system.usermanager.authenticate(user_data["username"], user_data["password"])

        response=self.user_api.cloudapi.accounts.get(self.response.json())
        self.assertEqual(response.status_code,get_code)

        data,response = self.user_api.cloudapi.cloudspaces.create(accountId=self.response.json(), location=self.location, access=user_data["username"])
        self.assertEqual(response.status_code,cloudspace_code)

        new_account_name = self.utils.random_string()
        response=self.user_api.cloudapi.accounts.update(accountId=self.response.json(),name=new_account_name)
        self.assertEqual(response.status_code, update_code)


      
    def test004_delete_account(self):
        """ OVC-000
        *Test case for deleting account.*

        **Test Scenario:**

        #. Create account [C1] .
        #. Delete account [C1], should succeed.
        #. Try to get [C1], should has destroyed status.
        #. Delete account [C1] again, should fail.
        """
        self.log.info("Delete account [C1], should succeed.")
        response = self.api.cloudbroker.account.delete(self.response.json())
        self.assertEqual(response.status_code, 200)
        self.CLEANUP['accounts'].remove(self.response.json())

        self.log.info("Try to get [C1], should has destroyed status.")
        response= self.api.cloudapi.accounts.get(self.response.json())
        self.assertEqual(response.json()["status"],"DESTROYED")

        self.log.info("Delete account [C1] again, should fail.")
        response = self.api.cloudbroker.account.delete(self.response.json())
        self.assertEqual(response.status_code, 404)

    def test005_delete_accounts(self):
        """ OVC-000
        *Test case for deleting multiple account.*

        **Test Scenario:**

        #. Create accounts [C1],[C2] , [C3] and [C4], should succeed .
        #. Delete account [C1], should succeed.
        #. Delete accounts [C1], [C2], should fail.
        #. Delete [C2] and [C3] accounts using delete acoounts api, should succeed. 
        #. Check that the four acounts deleted ,should succeed.
        """
        accounts=[self.response.json()]
        for _ in range(3):
            data,response=self.api.cloudbroker.account.create(self.user)
            accounts.append(response.json())
        response= self.api.cloudbroker.account.delete(accounts[0])
        self.assertEqual(response.status_code, 200)
        self.CLEANUP['accounts'].remove(self.response.json())
        
        response= self.api.cloudbroker.account.deleteAccounts([accounts[1],accounts[0]])
        self.assertEqual(response.status_code, 404)

        response= self.api.cloudbroker.account.deleteAccounts([accounts[2],accounts[3]])
        self.assertEqual(response.status_code, 200)

        for accountID in accounts:
            response = self.api.cloudapi.accounts.get(accountID)
            self.assertEqual(response.json()["status"],"DESTROYED")

    def test006_disable_non_exist_account(self):
        """ OVC-000
        *Test case for disable non-exist account .*

        **Test Scenario:**
        #. Disable non-exist account, should fail.
        """
   
        self.log.info("Disable non-exist account, should fail.")
        random_account= random.randint(3000,5000)
        response= self.api.cloudbroker.account.disable(random_account)
        self.assertEqual(response.status_code, 404)  


    def test007_disable_deleted_account(self):
        """ OVC-000
        *Test case for disable deleted  account .*

        **Test Scenario:**

        #. Disable deleted account ,should fail.
        
        """
   
        self.log.info("Disable deleted account ,should fail.")
        response= self.api.cloudbroker.account.delete(self.response.json())
        self.assertEqual(response.status_code, 200)
        self.CLEANUP['accounts'].remove(self.response.json())

        response= self.api.cloudbroker.account.disable(self.response.json())
        self.assertEqual(response.status_code, 404)


    def test008_enable_non_exist_account(self):
        """ OVC-000
        *Test case for  enable  non-exist account .*

        **Test Scenario:**
        #. Enable non-exist account, should fail.
        
        """
        self.log.info("Enable non-exist account, should fail.")
        random_account= random.randint(3000,5000)
        response= self.api.cloudbroker.account.enable(random_account)
        self.assertEqual(response.status_code, 404)  

    def test009_enable_deleted_acount(self):
        """ OVC-000
        *Test case for enable deleted account .*

        **Test Scenario:**
        #. Enable deleted account ,should fail.
        
        """

        self.log.info("Enable Deleted account, should fail.")
        response= self.api.cloudbroker.account.delete(self.response.json())
        self.assertEqual(response.status_code, 200)
        self.CLEANUP['accounts'].remove(self.response.json())

        response= self.api.cloudbroker.account.enable(self.response.json())
        self.assertEqual(response.status_code, 404)


    def test010_account_disable_and_enable(self):
        """ OVC-000
        *Test case for disable and enable account .*

        **Test Scenario:**
        #. Create account [C1] and user[U1].
        #. Disable account [C1], should succeed.
        #. Try to create cloudspace on [C1], should fail.
        #. Enable account [C1], should succeed.
        #. Try to create cloudspace on [C1], should succeed.

        """

        self.log.info(" Create account [C1] and user[U1].")
        data,response=self.api.cloudbroker.account.create(self.user)
        c1_id=response.json()
        self.CLEANUP['accounts'].append(c1_id)
        user_data,response = self.api.cloudbroker.user.create(groups=["user"])
        self.CLEANUP['users'].append(user_data["username"])
        self.user_api.system.usermanager.authenticate(user_data["username"], user_data["password"])
        data, response = self.api.cloudbroker.account.addUser(username=user_data["username"], accountId=c1_id,accesstype="ARCXDU")
        self.assertEqual(response.status_code, 200)
        
        self.log.info("Disable account [C1], should succeed.")
        response= self.api.cloudbroker.account.disable(c1_id)
        self.assertEqual(response.status_code, 200)    

        self.log.info("Try to create cloudspace on [C1], should fail.")
        data,response = self.user_api.cloudapi.cloudspaces.create(accountId=c1_id, location=self.location, access=user_data["username"])
        self.assertEqual(response.status_code,403, "Only READ actions can be executed on account (or one of its cloudspace or machines) with status DISABLED.")

        self.log.info(" Enable account [C1], should succeed.")
        response= self.api.cloudbroker.account.enable(c1_id)
        self.assertEqual(response.status_code, 200)    

        self.log.info("Try to create cloudspace on [C1], should succeed.")
        data,response = self.user_api.cloudapi.cloudspaces.create(accountId=c1_id, location=self.location, access=self.user)
        self.assertEqual(response.status_code,200)

    def test011_Update_non_exist_account(self):
        """ OVC-000
        *Test case for Update account .*

        **Test Scenario:**       
        #. Update name of non-exist account [C1],should fail.
        """
        random_account= random.randint(3000,5000)

        self.log.info("update non-exist account, should fail.")      
        data, response= self.api.cloudbroker.account.update(random_account)
        self.assertEqual(response.status_code, 404)


    @unittest.skip("https://github.com/0-complexity/openvcloud/issues/1355")
    def test012_Update_deleted_account(self):
        """ OVC-000
        *Test case for Update deleted account .*

        **Test Scenario:**       
        #. Update deleted account. should fail.
        """

        self.log.info(" Update deleted account. should fail.")
        response= self.api.cloudbroker.account.delete(self.response.json())
        self.assertEqual(response.status_code, 200)
        self.CLEANUP['accounts'].remove(self.response.json())

        data, response= self.api.cloudbroker.account.update(self.response.json())
        self.assertEqual(response.status_code, 404)


    def test013_Update_account(self):
        """ OVC-000
        #. Create account [C1].
        #. Update account [C1] name, should succeed.
        #. Check that account name updated, should succeed.
         
        """
        self.log.info(" Update account [C1] name, should succeed.")
        data,response= self.api.cloudbroker.account.update(self.response.json())
        self.assertEqual(response.status_code, 200)    

        self.log.info("Check that account name updated, should succeed.")
        response = self.api.cloudapi.accounts.get(self.response.json())
        self.assertEqual(data["name"], response.json()["name"])