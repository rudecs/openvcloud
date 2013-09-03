from JumpScale import j
from cloudapi_accounts_osis import cloudapi_accounts_osis
from cloudbrokerlib import authenticator


class cloudapi_accounts(cloudapi_accounts_osis):

    """
    API Actor api for managing account

    """

    def __init__(self):

        self._te = {}
        self.actorname = "accounts"
        self.appname = "cloudapi"
        cloudapi_accounts_osis.__init__(self)
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @authenticator.auth(acl='A')
    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountId id of the account
        param:userId id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        account = self.cb.models.cloudspace.new()
        account.dict2obj(self.cb.model_account_get(accountId))
        acl = account.new_acl()
        acl.userGroupId = userId
        acl.type = 'U'
        acl.right = accesstype
        return self.cb.models.account.set(account.obj2dict())

    @authenticator.auth(acl='S')
    def create(self, name, access, **kwargs):
        """
        Create a extra an account
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        result int
        """
        account = self.cb.models.account.new()
        account.name = name
        for userid in access:
            ace = account.new_acl()
            ace.userGroupId = userid
            ace.type = 'U'
            ace.right = 'CXDRAU'
        return self.cb.models.account.set(account.obj2dict())


    @authenticator.auth(acl='S')
    def delete(self, accountId, **kwargs):
        """
        Delete an account
        param:accountId id of the account
        result bool,
        """
        return self.cb.model_account_delete(accountId)

    @authenticator.auth(acl='R')
    def get(self, accountId, **kwargs):
        """
        get account.
        param:accountId id of the account
        result dict
        """
        #put your code here to implement this method
        return self.cb.model_account_get(accountId)

    @authenticator.auth(acl='A')
    def deleteUser(self, accountId, userId, **kwargs):
        """
        Delete a user from the account
        param:acountId id of the account
        param:userId id of the user to remove
        result

        """
        account = self.cb.model_account_get(accountId)
        change = False
        for ace in account['acl'][:]:
            if ace['userGroupId'] == userId:
                account['acl'].remove(ace)
                change = True
        if change:
            self.cb.models.account.set(account)
        return change

    def list(self, **kwargs):
        """
        List accounts.
        result [],

        """
#TODO implement dynamic filter here based on user access
        return self.cb.model_account_list()

    @authenticator.auth(acl='A')
    def update(self, accountId, name, **kwargs):
        """
        Update a account name
        param:accountId id of the account to change
        param:name name of the account
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method update")
