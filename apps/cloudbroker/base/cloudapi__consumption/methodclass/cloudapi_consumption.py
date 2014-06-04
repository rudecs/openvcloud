from JumpScale import j
from cloudbrokerlib import authenticator
from billingenginelib import pricing

class cloudapi_consumption(j.code.classGetBase()):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details

    """
    def __init__(self):
        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass

        self.models = Class()
        for ns in osiscl.listNamespaceCategories('billing'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'billing', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search

        self._te={}
        self.actorname="consumption"
        self.appname="cloudapi"
        #cloudapi_consumption_osis.__init__(self)
        
        self._pricing = pricing.pricing()
        

    @authenticator.auth(acl='R')
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
    def getBurnRate(self, accountId, **kwargs):
        """
        Get the hourly cost of the resources currently in use
        param:accountId id of the account
        result bool
        """
        return self._pricing.get_burn_rate(accountId)