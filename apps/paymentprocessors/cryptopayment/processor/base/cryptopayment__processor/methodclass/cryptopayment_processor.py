from JumpScale import j
import bitcoinrpc

class cryptopayment_processor(j.code.classGetBase()):
    """
    API Actor api for processing payments with cryptocurrency
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="processor"
        self.appname="cryptopayment"
        #cryptopayment_processor_osis.__init__(self)

        osiscl = j.core.osis.getClient()

        class Class():
            pass
        
        self.models = Class()
        for ns in osiscl.listNamespaceCategories('cryptopayment'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cryptopayment', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search
            
        
        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search

    def _get_wallet_connection(self,coin):
        if (coin == 'BTC'):
            con = bitcoinrpc.connect_to_remote('bitcoinrpc', '3hze4wu5Bro9UKXXFN2Jhr3N1zqJzMpoa5sWpztA2NiW', '127.0.0.1', 8332)
        elif (coin =='LTC'):
            con =  bitcoinrpc.connect_to_remote('litecoinrpc','2Lh856DN1SuBSburBeirD1hgoyP6SZkRCbDzuc4oEkYN' , '127.0.0.1', 9332)
        else:
            con = None
        return con
        
    def _get_last_processed_block(coin):
        query = {'fields': ['coin', 'hash', 'blocktime']}
        query['query'] = {'term': {"accountId": accountId, "currency":currency}}
        query['size'] = 1
        query['sort'] = [{ "blocktime" : {'order':'desc', 'ignore_unmapped' : True}}]
        results = self.models.processedblock.find(ujson.dumps(query))['result']
        processedblocks = [res['fields'] for res in results]
        if len(result) > 0:
            return processedblocks[0]
        else:
            return ''
        
    def _getNetworkTransactionsSince(coin, block_hash):
        con = self._get_wallet_connection(coin)
        rawtransactions = con.listsinceblock(block_hash)
        transactions = [{'txid':t.txid,'address':t.address,'amount':t.amount,'time':t.time,'timereceived':t.timereceived,'confirmations':t.confirmations} for t in rawtransactions['transactions'] if t.category == 'receive']
        return {'lastblock':rawtransactions['lastblock'],'transactions':transactions}
    
    def _get_credit_transaction(self, coin, reference):
        query = {'fields': ['time', 'currency', 'amount', 'credit','reference', 'status', 'comment']}
        query['query'] = {'term': {"currency": coin, 'reference':reference}}
        results = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        transactions = [res['fields'] for res in results]
        return None if len(transactions) == 0 else transactions[0]
   
    def _getAddressForAccount(self, accountId, currency):
        """
        Gets the address assigned to an account, if there is none registered, assign it to the account passed before returning it.
        param:accountId account
        param:currency code of the cryptocurrency (LTC or BTC)
        result dict,,
        """
        query = {'fields': ['id', 'coin', 'accountId']}
        query['query'] = {'term': {"accountId": accountId, "currency":currency}}
        query['size'] = 1
        results = self.models.paymentaddress.find(ujson.dumps(query))['result']
        addresses = [res['fields'] for res in results]
        return None if len(addresses) == 0 else addresses[0]
     
    def _getValueForCurrency(self, currency, time):
        #TODO: get real(stored) value
        if (currency == 'BTC'):
            return 800.0
        elif (currency == 'LTC'):
            return 20.0
        else:
            return None
    
    def process(self, coin, **kwargs):
        """
        Process the transactions for a given currency (should become jumpscript)
        
        param:coin code of the currency to process transactions from (LTC and BTC currently supported)
        """
        block_hash = self._get_last_processed_block(coin)
        response = self._getNetworkTransactionsSince(coin, block_hash)
        
        processedblock = self.models.processedblock.new()
        processedblock.coin = coin
        processedblock.hash = response['lastblock']
        processedblock.time = response['time']
        
        networktransactions = response['transactions']
        
        for networktransaction in networktransactions:
            creditTransaction = self._get_credit_transaction(coin, networktransaction['txid'])
            if creditTransaction is None:
                account = self._getAddressForAccount(networktransaction['address'])
                if account is None: #A transaction in the wallet but not an account assigned on the address yet
                    continue
                
                transaction = self.cloudbrokermodels.credittransaction.new()
                transaction.accountId = account
                transaction.time = networktransaction['time']
                transaction.currency = coin
                transaction.amount = float(networktransaction['amount'])
                transaction.comment = 'Credit'
                transaction.reference = networktransaction['txid']                                                                          
                                
                transaction.credit = transaction['amount'] * self._getValueForCurrency(coin, transaction.time)
                transaction.status = 'PROCESSED' if (networktransaction['confirmations'] > 0) else 'UNCONFIRMED'
                self.cloudbrokermodels.credittransaction.set(credittransaction)
            else:
                if ((not creditTransaction.status == 'PROCESSED') and (networktransaction['confirmations'] > 0)):
                    creditTransaction.status = 'PROCESSED'
                    self.cloudbrokermodels.credittransaction.set(credittransaction)
                    
        self.models.processedblock.set(processedblock)