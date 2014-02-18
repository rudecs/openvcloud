from JumpScale import j

class cryptopayment_paymentaddress(j.code.classGetBase()):
    """
    API Actor api for processing paymentaddresses
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="paymentaddress"
        self.appname="cryptopayment"
        
        osiscl = j.core.osis.getClient(user='root')

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
        newAddress = self.models.paymentaddress.new()
        newAddress.id = address
        newAddress.currency = currency
        newAddress.accountId = ''
        #TODO: add to wallet
        self.models.paymentaddress.set(newAddress)
    