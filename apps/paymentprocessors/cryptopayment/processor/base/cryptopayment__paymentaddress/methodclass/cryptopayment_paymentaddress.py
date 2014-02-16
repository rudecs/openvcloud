from JumpScale import j

class cryptopayment_paymentaddress(j.code.classGetBase()):
    """
    API Actor api for processing paymentaddresses
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="paymentaddress"
        self.appname="cryptopayment"
        #cryptopayment_paymentaddress_osis.__init__(self)
    

        pass

    def create(self, address, currency, **kwargs):
        """
        Registers an address to be available for customers to make payments on.
        This needs to be a valid address for the given currency.
        param:address address
        param:currency code of the cryptocurrency (LTC or BTC)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method create")
    

    def getAddressForAccount(self, accountId, currency, **kwargs):
        """
        Gets the address assigned to an account, if there is none registered, assign it to the account passed before returning it.
        param:accountId account
        param:currency code of the cryptocurrency (LTC or BTC)
        result dict,,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getAddressForAccount")
    
