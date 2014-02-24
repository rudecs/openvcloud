from JumpScale import j
import time

class billingengine_billingengine(j.code.classGetBase()):
    """
    Actor for generating negative billing transactions based on cloudusage
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="billingengine"
        self.appname="billingengine"
        #billingengine_billingengine_osis.__init__(self)
    
        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass      
        
        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.cloudbrokermodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.cloudbrokermodels.__dict__[ns].find = self.cloudbrokermodels.__dict__[ns].search

    def _get_last_transaction_statement(self, accountId):
        #TODO
        pass

    def _update_usage(self, transaction_statement):
        #TODO
        pass
    
    def _save_transaction_statement(self,transaction_statement):
        #TODO
        pass
    
    def _find_earliest_billable_action_time(self, accountId):
        #TODO
        pass
    
    def _create_empty_transaction_statements(self, fromTime, untilTime):
        #TODO
        pass
    
    def createTransactionStaments(self, accountId, **kwargs):
        """
        Generates the missing transactions for an account
        param:accountId id of the account
        """
        now = int(time.time())
        last_transaction_statement = self._get_last_transaction_statement(accountId)
        last_transaction_time = None
        if not last_transaction_statement is None:
            self._update_usage(last_transaction_statement)
            self._save_transaction_statement(last_transaction_statement)
            last_transaction_time = last_transaction_statement.time
        else:
            last_transaction_time = self._find_earliest_billable_action_time(accountId)
            
        for transaction_statement in self._create_empty_transaction_statements(last_transaction_time.time, now):
            self._update_usage(transaction_statement)
            self._save_transaction_statement(transaction_statement)
        

    def updateBalance(self, accountId, **kwargs):
        """
        Updates the ballance for an account given the credit/debit transactions
        param:accountId id of the account
        """
        #For now, sum here, as of ES 1.0, can be done there
        query = {'fields': ['time', 'credit', 'status']}
        query['query'] = {'bool':{'must':[{'term': {"accountId": accountId}}],'must_not':[{'term':{'status':'UNCONFIRMED'.lower()}}]}}
        results = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        history = [res['fields'] for res in results]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
            #TODO: put in processed (but only save after updating the balance
            
        newbalance = self.cloudbrokermodels.creditbalance.new()
        newbalance.accountId = accountId
        newbalance.time = int(time.time())
        newbalance.credit = balance
        self.cloudbrokermodels.creditbalance.set(newbalance)
