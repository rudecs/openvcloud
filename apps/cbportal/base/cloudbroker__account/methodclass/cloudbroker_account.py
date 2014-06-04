from JumpScale import j
import time
import JumpScale.grid.osis

class cloudbroker_account(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="account"
        self.appname="cloudbroker"
        self._cb = None
        self._models = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    def disable(self, accountname, reason, **kwargs):
        """
        Disable an account
        param:acountname name of the account
        param:reason reason of disabling
        result

        """
        account = self.models.account.simpleSearch({'name':accountname})
        if not account:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'
        else:
            account = account[0]
            account['deactivationTime'] = time.time()
            account['status'] = 'DISABLED'
            self.models.account.set(account)