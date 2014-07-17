from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator
from billingenginelib import pricing

class cloudapi_consumption(j.code.classGetBase()):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details

    """
    def __init__(self):

        self._te={}
        self.actorname="consumption"
        self.appname="cloudapi"
        self._cb = None
        self._models = None
        #cloudapi_consumption_osis.__init__(self)
        self._pricing = pricing.pricing()

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
        

    @authenticator.auth(acl='R')
    @audit()
    def get(self, accountId, reference, **kwargs):
        """
        Gets detailed consumption for a specific creditTransaction.
        param:accountId id of the account
        param:reference id of the billingstatement
        result bool
        """
        billingstatement = self.models.billingstatement.get(reference)
        if str(billingstatement.accountId) != accountId:
            ctx = kwargs['ctx']
            ctx.start_response('401 Unauthorized', [])
            return ""
        return billingstatement.dump()

    @authenticator.auth(acl='R')
    @audit()
    def getBurnRate(self, accountId, **kwargs):
        """
        Get the hourly cost of the resources currently in use
        param:accountId id of the account
        result bool
        """
        return self._pricing.get_burn_rate(accountId)
