from JumpScale import j
import time
import JumpScale.grid.osis

class cloudbroker_account(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="account"
        self.appname="cloudbroker"

    def disable(self, accountname, reason, **kwargs):
        """
        Disable an account
        param:acountname name of the account
        param:reason reason of disabling
        result

        """
        cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        account = cbcl.account.simpleSearch({'name':accountname})
        if not account:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'
        else:
            account = account[0]
            account['deactivationTime'] = time.time()
            account['status'] = 'DISABLED'
            cbcl.account.set(account)