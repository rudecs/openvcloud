from JumpScale import j
from cloudbrokerlib import authenticator
import ujson

class cloudapi_payments(object):
    """
    API Actor api for performing payments with cryptocurrency

    """
    
    def __init__(self):
        osiscl = j.clients.osis.getByInstance('main')

        class Class():
            pass
        
        self.models = Class()
        for ns in osiscl.listNamespaceCategories('cryptopayment'):
            self.models.__dict__[ns] = (j.clients.osis.getForCategory(osiscl, 'cryptopayment', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search
    
    
    
    def _assignAddressToAccount(self,accountId, currency):
        query = {'fields': ['id', 'currency', 'accountId']}
        query['query'] = { 'bool': { 'must': [{'term': {'accountId': '0'}},{'term': {'currency':currency.lower()}}] } }
        query['size'] = 100
        results = self.models.paymentaddress.find(ujson.dumps(query))['result']
        addresses = [res['fields'] for res in results]
        assignedAddress = None
        for address in addresses:
            addressCandidate = self.models.paymentaddress.get(address['id'])
            if not addressCandidate.accountId == 0:
                continue
            addressCandidate.accountId = accountId
            self.models.paymentaddress.set(addressCandidate)
            #validate it is indeed assigned to this accountId
            addressCandidate = self.models.paymentaddress.get(address['id'])
            if not addressCandidate.accountId == accountId:
                continue
            
            assignedAddress = addressCandidate
        
        return None if assignedAddress is None else {'id':assignedAddress.id}

    def _getAddressForAccount(self, accountId, currency):
        """
        Gets the address assigned to an account, if there is none registered, assign it to the account passed before returning it.
        param:accountId account
        param:currency code of the cryptocurrency (LTC or BTC)
        result dict,,
        """
        query = {'fields': ['id', 'currency', 'accountId']}
        query['query'] = {'bool':{'must':[{'term': {"accountId": accountId}},{'term':{"currency":currency.lower()}}]}}
        query['size'] = 1
        results = self.models.paymentaddress.find(ujson.dumps(query))['result']
	addresses = [res['fields'] for res in results]
        if len(addresses) == 0:
            address = self._assignAddressToAccount(accountId, currency)
        else:
            address = addresses[0]
            
        return address
    
    def _getValueForCurrency(self, currency):
        #TODO: get real(stored) value
        if (currency == 'BTC'):
            return 800.0
        elif (currency == 'LTC'):
            return 20.0
        else:
            return None
    
    @authenticator.auth(acl='R')
    def getPaymentInfo(self, accountId, coin, **kwargs):
        """
        Get the info required for making a payment
        
        param:accountId id of the account
        param:coin the code of the currency you want to make a payment with (LTC or BTC currently supported)
        result:dict A json dict containing 'address', 'value' and 'coin':coin
        """
        address = self._getAddressForAccount(accountId, coin)
        
        if address is None:
            ctx = kwargs['ctx']
            ctx.start_response("503 Service Unavailable", [])
            return 'Temporarily unavailable'
        
        value = self._getValueForCurrency(coin)
        
        return {'address':address['id'],'value':value, 'coin':coin}
