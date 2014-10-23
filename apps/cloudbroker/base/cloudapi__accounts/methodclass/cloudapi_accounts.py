from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
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
    @audit()
    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountId id of the account
        param:userId id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        if not self.models.account.exists(accountId):
            return False
        account = self.models.account.get(accountId)
        acl = account.new_acl()
        acl.userGroupId = userId
        acl.type = 'U'
        acl.right = accesstype
        return self.models.account.set(account)

    @authenticator.auth(acl='S')
    @audit()
    def create(self, name, access, **kwargs):
        """
        Create a extra an account
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        result int
        """
        account = self.models.account.new()
        account.name = name
        if isinstance(access, basestring):
            access = [ access ]
        for userid in access:
            ace = account.new_acl()
            ace.userGroupId = userid
            ace.type = 'U'
            ace.right = 'CXDRAU'
        return self.models.account.set(account)[0]


    @authenticator.auth(acl='S')
    @audit()
    def delete(self, accountId, **kwargs):
        """
        Delete an account
        param:accountId id of the account
        result bool,
        """
        return self.models.account.delete(accountId)

    @authenticator.auth(acl='R')
    @audit()
    def get(self, accountId, **kwargs):
        """
        get account.
        param:accountId id of the account
        result dict
        """
        #put your code here to implement this method

        return self.models.account.get(accountId)

    @authenticator.auth(acl='R')
    @audit()
    def listTemplates(self, accountId, **kwargs):
        """
        List templates which can be managed by this account
        param:accountId id of the account
        result dict
        """
        fields = ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        query = {'accountId': int(accountId)}
        results = self.models.image.search(query)[1:]
        self.cb.extensions.imp.filter(results, fields)
        return results

    @authenticator.auth(acl='A')
    @audit()
    def deleteUser(self, accountId, userId, **kwargs):
        """
        Delete a user from the account
        param:acountId id of the account
        param:userId id of the user to remove
        result

        """
        account = self.models.account.get(accountId)
        change = False
        for ace in account.acl:
            if ace.userGroupId == userId:
                account.acl.remove(ace)
                change = True
        if change:
            self.models.account.set(account)
        return change

    @audit()
    def list(self, **kwargs):
        """
        List accounts.
        result [],

        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        fields = ['id', 'name', 'acl']
        query = {'acl.userGroupId': user}
        accounts = self.models.account.search(query)[1:]
        self.cb.extensions.imp.filter(accounts, fields)
        return accounts

    @authenticator.auth(acl='A')
    @audit()
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
    @audit()
    def getCreditBalance(self, accountId, **kwargs):
        """
        Get the current available credit
        param:accountId id of the account
        result:dict A json dict containing the available credit
        """
        # For now, don't get the balance statement, just calculate it
        #query = {'fields': ['time', 'credit']}
        #query['query'] = {'term': {"accountId": accountId}}
        #query['size'] = 1
        #query['sort'] = [{ "time" : {'order':'desc', 'ignore_unmapped' : True}}]
        #results = self.models.creditbalance.find(ujson.dumps(query))['result']
        #balance = [res['fields'] for res in results]
        
        #return balance[0] if len(balance) > 0 else {'credit':0, 'time':-1}

        fields = ['time', 'credit', 'status']
        query = {'accountId': int(accountId), 'status': {'$ne': 'UNCONFIRMED'}}
        history = self.models.credittransaction.search(query)[1:]
        self.cb.extensions.imp.filter(history, fields)
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
        import time
        return {'credit':balance, 'time':int(time.time())}

    @authenticator.auth(acl='R')
    @audit()
    def getCreditHistory(self, accountId, **kwargs):
        """
        Get all the credit transactions (positive and negative) for this account.
        param:accountId id of the account
        result:[] A json list with the transactions details.
        """

        fields = ['time', 'currency', 'amount', 'credit','reference', 'status', 'comment']
        query = {"accountId": int(accountId)}
        history = self.models.credittransaction.search(query)[1:]
        self.cb.extensions.imp.filter(history, fields)
        return history
