from JumpScale import j
import bitcoinrpc

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


    
    def _get_wallet_connection(self,coin):
        if (coin == 'BTC'):
            con = bitcoinrpc.connect_to_remote('bitcoinrpc', '3hze4wu5Bro9UKXXFN2Jhr3N1zqJzMpoa5sWpztA2NiW', '127.0.0.1', 8332)
        elif (coin =='LTC'):
            con =  bitcoinrpc.connect_to_remote('litecoinrpc','2Lh856DN1SuBSburBeirD1hgoyP6SZkRCbDzuc4oEkYN' , '127.0.0.1', 9332)
        else:
            con = None
        return con

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
        
        walletconnection = self._get_wallet_connection(currency)
        walletconnection.proxy.importaddress(address,'ListenFor',False)
        
        self.models.paymentaddress.set(newAddress)
        return newAddress