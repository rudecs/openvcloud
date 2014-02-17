from JumpScale import j

class cryptopayment_paymentaddress(j.code.classGetBase()):
    """
    API Actor api for processing paymentaddresses
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="paymentaddress"
        self.appname="cryptopayment"
        
        osiscl = j.core.osis.getClient()

        class Class():
            pass
        
        self.models = Class()
        for ns in osiscl.listNamespaceCategories('cryptopayment'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cryptopayment', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search

    def create(self, address, currency, **kwargs):
        """
        Registers an address to be available for customers to make payments on.
        This needs to be a valid address for the given currency.
        param:address address
        param:currency code of the cryptocurrency (LTC or BTC)
        """
        existingAddress = self.models.paymentaddress.get(address)
        if (not existingAddress is None):
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'Address already registered'
        
        newAddress = self.models.paymentAddress.new()
        newAddress.id = address
        newAddress.currency = currency
        newAddress.accountId = ''
        #TODO: add to wallet
        self.models.paymentaddress.set(newAddress)
    
    def _assignAddressToAccount(self,accountId, currency):
        query = {'fields': ['id', 'coin', 'accountId']}
        query['query'] = {'term': {"accountId": '', "currency":currency}}
        query['size'] = 100
        results = self.models.paymentAddress.find(ujson.dumps(query))['result']
        addresses = [res['fields'] for res in results]
        assignedAddress = None
        for address in addresses:
            addressCandidate = self.models.paymentAddress.get(address.address)
            if not addressCandidate.accountId == '':
                continue
            addressCandidate.accountId = accountId
            self.models.paymentAddress.set(addressCandidate)
            #validate it is indeed assigned to this accountId
            addressCandidate = self.models.paymentAddress.get(address.address)
            if not addressCandidate.accountId == accountId:
                continue
            
            assignedAddress = addressCandidate
        
        return addressCandidate

    def getAddressForAccount(self, accountId, currency, **kwargs):
        """
        Gets the address assigned to an account, if there is none registered, assign it to the account passed before returning it.
        param:accountId account
        param:currency code of the cryptocurrency (LTC or BTC)
        result dict,,
        """
        query = {'fields': ['id', 'coin', 'accountId']}
        query['query'] = {'term': {"accountId": accountId, "currency":currency}}
        query['size'] = 1
        results = self.models.paymentAddress.find(ujson.dumps(query))['result']
        addresses = [res['fields'] for res in results]
        if len(addresses) == 0:
            address = self._assignAddressToAccount(accountId, currency)
        else:
            address = addresses[0]
        if address is None:
            ctx = kwargs['ctx']
            ctx.start_response("503 Service Unavailable", [])
            return 'Temporarily unavailable'
        
        return address
        
    
