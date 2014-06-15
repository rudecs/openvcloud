from JumpScale import j
import time
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth

class cloudbroker_account(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="account"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')

    def _checkAccount(self, accountname, ctx):
        account = self.cbcl.account.simpleSearch({'name':accountname})
        if not account:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return False, 'Account name not found'
        return True, account[0]

    @auth(['level1','level2'])
    def disable(self, accountname, reason, **kwargs):
        """
        Disable an account
        param:acountname name of the account
        param:reason reason of disabling
        result
        """
        ctx = kwargs["ctx"]
        check, result = self._checkAccount(accountname, ctx)
        if not check:
            return result
        else:
            account = result
            account['deactivationTime'] = time.time()
            account['status'] = 'DISABLED'
            self.cbcl.account.set(account)
            return True

    @auth(['level1','level2'])
    def enable(self, accountname, reason, **kwargs):
        """
        Enable an account
        param:acountname name of the account
        param:reason reason of enabling
        result
        """
        ctx = kwargs["ctx"]
        check, result = self._checkAccount(accountname, ctx)
        if not check:
            return result
        else:
            account = result
            if account['status'] != 'DISABLED':
                ctx = kwargs["ctx"]
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response("400", headers)
                return 'Account is not disabled'

            account['status'] = 'CONFIRMED'
            self.cbcl.account.set(account)
            return True

    @auth(['level1','level2'])
    def delete(self, accountname, reason, **kwargs):
        """
        Complete delete an acount from the system
        """
        ctx = kwargs["ctx"]
        check, result = self._checkAccount(accountname, ctx)
        if not check:
            return result
        else:
            accountId = result['id']
            query = dict()
            query['query'] = {'bool':{'must':[
                                          {'term': {'accountId': accountId}}
                                          ],
                                  'must_not':[
                                              {'term':{'status':'DESTROYED'.lower()}},
                                              ]
                                  }
                          }
            cloudspaces = self.cbcl.cloudspace.search(query)['result']
            if cloudspaces:
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response("403", headers)
                return 'Can not remove account which still has cloudspaces'
            self.cbcl.account.delete(result['id'])
            return True


