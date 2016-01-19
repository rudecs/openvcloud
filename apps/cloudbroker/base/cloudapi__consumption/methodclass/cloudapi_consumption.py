from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator
from billingenginelib import pricing

class cloudapi_consumption(object):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details

    """
    def __init__(self):
        self.models = j.clients.osis.getNamespace('billing')
        self._pricing = pricing.pricing()

    @audit()
    def get(self, accountId, reference, **kwargs):
        """
        Gets detailed consumption for a specific creditTransaction

        :param accountId: id of the account
        :param reference: id of the billing statement
        :return dict with the consumption details
        """
        accountId = int(accountId)
        billingstatement = self.models.billingstatement.get(int(reference))
        if billingstatement.accountId != accountId:
            ctx = kwargs['ctx']
            ctx.start_response('401 Unauthorized', [])
            return ""
        return billingstatement.dump()

    @audit()
    def getBurnRate(self, accountId, **kwargs):
        """
        Get the hourly cost of the resources currently in use

        :param accountId: id of the account
        :return dict with the burn rate report
        """
        accountId = int(accountId)
        return self._pricing.get_burn_rate(accountId)
