from JumpScale import j
import bitcoinrpc
import ujson

class cryptopayment_processor(j.code.classGetBase()):
    """
    API Actor api for processing payments with cryptocurrency
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="processor"
        self.appname="cryptopayment"
        #cryptopayment_processor_osis.__init__(self)

        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass
        
        self.models = Class()
        for ns in osiscl.listNamespaceCategories('cryptopayment'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cryptopayment', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search
            
        
        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.cloudbrokermodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.cloudbrokermodels.__dict__[ns].find = self.cloudbrokermodels.__dict__[ns].search

    def _get_wallet_connection(self,coin):
        if (coin == 'BTC'):
            con = bitcoinrpc.connect_to_remote('bitcoinrpc', '3hze4wu5Bro9UKXXFN2Jhr3N1zqJzMpoa5sWpztA2NiW', '127.0.0.1', 8332)
        elif (coin =='LTC'):
            con =  bitcoinrpc.connect_to_remote('litecoinrpc','2Lh856DN1SuBSburBeirD1hgoyP6SZkRCbDzuc4oEkYN' , '127.0.0.1', 9332)
        else:
            con = None
        return con
        
    def _get_last_processed_block(self, currency):
        query = {'fields': ['coin', 'hash', 'blocktime']}
        query['query'] = {'term': {"currency":currency.lower()}}
        query['size'] = 1
        query['sort'] = [{ "blocktime" : {'order':'desc', 'ignore_unmapped' : True}}]
        results = self.models.processedblock.find(ujson.dumps(query))['result']
        processedblocks = [res['fields'] for res in results]
        if len(processedblocks) > 0:
            return processedblocks[0]
        else:
            return ''
        
    def _getNetworkTransactionsSince(self, coin, block_hash):
        con = self._get_wallet_connection(coin)
        rawtransactions = con.listsinceblock(block_hash)
        transactions = [{'txid':t.txid,'address':t.address,'amount':t.amount,'time':t.time,'timereceived':t.timereceived,'confirmations':t.confirmations} for t in rawtransactions['transactions'] if t.category == 'receive']
        return {'lastblock':rawtransactions['lastblock'],'transactions':transactions}
    
    def _set_last_processed_block(self, currency, block_hash):
        con = self._get_wallet_connection(currency)
        block_info = con.getblock(block_hash)
        
        processedblock = self.models.processedblock.new()
        processedblock.coin = currency
        processedblock.hash = block_hash
        processedblock.time = block_info['time']
        
        self.models.processedblock.set(processedblock)
    
    def _get_credit_transaction(self, coin, reference):
        query = {'fields': ['id', 'currency','reference']}
        query['query'] = {'bool':{'must':[{'term': {"currency": coin.lower()}},{'term':{ 'reference':reference.lower()}}]}}
        results = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        transactions = [res['fields'] for res in results]
        return None if len(transactions) == 0 else self.cloudbrokermodels.credittransaction.get(transactions[0]['id'])
   
    def _getAccountForAddress(self, address, currency):
        """
        Gets the account assigned to an aaddress
        param:address
        param:currency code of the cryptocurrency (LTC or BTC)
        result dict,,
        """
        query = {'fields': ['id', 'coin', 'accountId']}
        query['query'] = {'bool': {'must':[ {'term': {"id": address.lower()}},{'term':{"currency":currency.lower()}}]}}
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
    
    def process(self, currency, **kwargs):
        """
        Process the transactions for a given currency (should become jumpscript)
        
        param:coin code of the currency to process transactions from (LTC and BTC currently supported)
        """
        block_hash = self._get_last_processed_block(currency)
        response = self._getNetworkTransactionsSince(currency, block_hash)
        last_processed_block_hash = response['lastblock']
        
        
        networktransactions = response['transactions']
        
        for networktransaction in networktransactions:
            creditTransaction = self._get_credit_transaction(currency, networktransaction['txid'])
            if creditTransaction is None:
                account = self._getAccountForAddress(networktransaction['address'], currency)
                if account is None: #A transaction in the wallet but not an account assigned on the address yet
                    continue
                
                transaction = self.cloudbrokermodels.credittransaction.new()
                transaction.accountId = account
                transaction.time = networktransaction['time']
                transaction.currency = currency
                transaction.amount = float(networktransaction['amount'])
                transaction.comment = 'Credit'
                transaction.reference = networktransaction['txid']                                                                          
                                
                transaction.credit = transaction.amount * self._getValueForCurrency(currency, transaction.time)
                transaction.status = 'PROCESSED' if (networktransaction['confirmations'] > 0) else 'UNCONFIRMED'
                self.cloudbrokermodels.credittransaction.set(transaction)
            else:
                if ((not creditTransaction.status == 'PROCESSED') and (networktransaction['confirmations'] > 0)):
                    creditTransaction.status = 'PROCESSED'
                    self.cloudbrokermodels.credittransaction.set(creditTransaction)
                    
        self._set_last_processed_block(currency, last_processed_block_hash)
