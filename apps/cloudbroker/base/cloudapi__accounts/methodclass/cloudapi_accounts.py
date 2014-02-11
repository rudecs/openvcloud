from JumpScale import j
from cloudbrokerlib import authenticator
import ujson


class cloudapi_accounts(object):
    """
    API Actor api for managing account

    """
    def __init__(self):

        self._te = {}
        self.actorname = "accounts"
        self.appname = "cloudapi"
        self._cb = None
        self._models = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

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
        account = self.cb.models.account.new()
        account.dict2obj(self.models.account.get(accountId))
        acl = account.new_acl()
        acl.userGroupId = userId
        acl.type = 'U'
        acl.right = accesstype
        return self.models.account.set(account)

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
        return self.models.account.set(account)[0]


    @authenticator.auth(acl='S')
    def delete(self, accountId, **kwargs):
        """
        Delete an account
        param:accountId id of the account
        result bool,
        """
        return self.models.account.delete(accountId)

    @authenticator.auth(acl='R')
    def get(self, accountId, **kwargs):
        """
        get account.
        param:accountId id of the account
        result dict
        """
        #put your code here to implement this method
        return self.models.account.get(accountId)

    @authenticator.auth(acl='A')
    def deleteUser(self, accountId, userId, **kwargs):
        """
        Delete a user from the account
        param:acountId id of the account
        param:userId id of the user to remove
        result

        """
        account = self.models.account.get(accountId)
        change = False
        for ace in account['acl'][:]:
            if ace['userGroupId'] == userId:
                account['acl'].remove(ace)
                change = True
        if change:
            self.models.account.set(account)
        return change

    def list(self, **kwargs):
        """
        List accounts.
        result [],

        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        query = {'fields': ['id', 'name', 'acl']}
        query['query'] = {'term': {"userGroupId": user}}
        results = self.models.account.find(ujson.dumps(query))['result']
        accounts = [res['fields'] for res in results]
        return accounts

    @authenticator.auth(acl='A')
    def update(self, accountId, name, **kwargs):
        """
        Update an account name
        param:accountId id of the account to change
        param:name name of the account
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method update")
    
    @authenticator.auth(acl='R')
    def getCreditBalance(self, accountId, **kwargs):
        """
        Get the current available credit

        param:accountId id of the account
        result:dict A json dict containing the available credit
        """
        query = {'fields': ['time', 'credit']}
        query['query'] = {'term': {"accountId": accountId}}
        query['size'] = 1
        query['sort'] = [{ "time" : "desc"}]
        results = self.models.CreditHistory.find(ujson.dumps(query))['result']
        balance = [res['fields'] for res in results]
        
        return balance[0] if len(balance) > 0 else {'credit':0, 'time':-1}
    
    @authenticator.auth(acl='R')
    def getCreditHistory(self, accountId, **kwargs):
        """
        Get all the credit transactions (positive and negative) for this account.
        
        param:accountId id of the account
        result:[] A json list with the transactions details.
        """
        query = {'fields': ['time', 'currency', 'amount', 'credit','reference', 'status', 'comment']}
        query['query'] = {'term': {"accountId": accountId}}
        results = self.models.CreditHistory.find(ujson.dumps(query))['result']
        history = [res['fields'] for res in results]
        return history