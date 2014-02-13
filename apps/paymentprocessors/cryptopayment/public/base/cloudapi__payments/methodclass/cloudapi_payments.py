from JumpScale import j
from cloudbrokerlib import authenticator
import ujson


class cloudapi_payments(object):
    """
    API Actor api for performing payments with cryptocurrency

    """
    
    @authenticator.auth(acl='R')
    def getPaymentInfo(self, accountId, coin, **kwargs):
        """
        Get all the credit transactions (positive and negative) for this account.
        
        param:accountId id of the account
        param:coin the code of the currency you want to make a payment with (LTC or BTC currently supported)
        result:dict A json dict containing 'address', 'value' and 'coin':coin
        """
        return {'address':'abcd','value':800.0, 'coin':coin}