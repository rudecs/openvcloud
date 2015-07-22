from JumpScale import j
import unittest
import uuid
from JumpScale.baselib.http_client.HttpClient import HTTPError
from lib import helper

CLEANUP = []

class AccountTest(helper.BaseTest):
    accountId = None
    password = None
    username = None
    session = None
    cloudspace = None

    def test_1_registerAccount(self):
        AccountTest.username = str(uuid.uuid4()).replace('-', '')[0:10]
        AccountTest.password = str(uuid.uuid4())
        email = "%s@example.com" % str(uuid.uuid4())
        location = self.get_location()['locationCode']
        AccountTest.accountId = self.api.cloudbroker.account.create(self.username, self.username, email, self.password, location)
        self.assertTrue(self.accountId)
        CLEANUP.append(self.username)

    def test_2_login_with_account(self):
        session = self.api.cloudapi.users.authenticate(self.username, self.password)
        self.assertTrue(session)
        AccountTest.session = session

    def test_3_check_cloudspace(self):
        api = j.clients.portal.get2(secret=self.session)
        cloudspaces = api.cloudapi.cloudspaces.list()
        self.assertEqual(len(cloudspaces), 1)
        cloudspace = cloudspaces[0]
        self.assertEqual(cloudspace['status'], 'VIRTUAL')
        AccountTest.cloudspace = cloudspace['id']

    def test_4_grant_access(self):
        whoami = self.api.system.usermanager.whoami()
        api = j.clients.portal.get2(secret=self.session)
        api.cloudapi.accounts.addUser(accountId=self.accountId, userId=whoami, accesstype='CDXRAU')
        accounts = self.api.cloudapi.accounts.list()
        self.assertTrue(accounts)
        accountids = [account['id'] for account in accounts]
        self.assertIn(self.accountId, accountids)

    def test_5_revoke_acess(self):
        whoami = self.api.system.usermanager.whoami()
        api = j.clients.portal.get2(secret=self.session)
        api.cloudapi.accounts.deleteUser(accountId=self.accountId, userId=whoami)
        accounts = self.api.cloudapi.accounts.list()
        accountids = [account['id'] for account in accounts]
        self.assertNotIn(self.accountId, accountids)


def tearDown():
    api = helper.API()
    for accountname in CLEANUP:
        api.cloudbroker.account.delete(accountname, accountname)


if __name__ == '__main__':
    unittest.main()
