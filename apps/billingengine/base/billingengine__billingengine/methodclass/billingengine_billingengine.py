from JumpScale import j
import time, ujson
from datetime import datetime
import calendar

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
        
        self.billingenginemodels = Class()
        for ns in osiscl.listNamespaceCategories('billingengine'):
            self.billingenginemodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'billingengine', ns))
            self.billingenginemodels.__dict__[ns].find = self.billingenginemodels.__dict__[ns].search
                
        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.cloudbrokermodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.cloudbrokermodels.__dict__[ns].find = self.cloudbrokermodels.__dict__[ns].search

    def _get_last_billing_statement(self, accountId):
        query = {'fields': ['fromTime', 'accountId','id']}
        query['query'] = {'term': {"accountId": accountId}}
        query['size'] = 1
        query['sort'] = [{ "fromTime" : {'order':'desc', 'ignore_unmapped' : True}}]
        results = self.billingenginemodels.billingstatement.find(ujson.dumps(query))['result']
        if len(results) > 0:
            return self.billingenginemodels.billingstatement.get(results[0]['id'])
        else:
            return None

    def _update_usage(self, billing_statement):
        #TODO
        pass
    
    def _get_credit_transaction(self, currency, reference):
        query = {'fields': ['id', 'currency','reference']}
        query['query'] = {'bool':{'must':[{'term': {"currency": currency.lower()}},{'term':{ 'reference':reference.lower()}}]}}
        transactions = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        return None if len(transactions) == 0 else self.cloudbrokermodels.credittransaction.get(transactions[0]['id'])   

    def _save_billing_statement(self,billing_statement):
        self.billingenginemodels.billingstatement.set(biling_statement)
        creditTransaction = self._get_credit_transaction('USD', reference)
        if creditTransaction is None:
            creditTransaction = self.cloudbrokermodels.credittransaction.new()
            creditTransaction.currency = 'USD'
            creditTransaction.reference = billing_statement.id
            creditTransaction.status = 'DEBIT'
        
        creditTransaction.amount = -billing_statement.totalCost
        creditTransaction.credit = -billing_statement.totalCost
        self.cloudbrokermodels.credittransaction.set(creditTransaction)
    
    def _find_earliest_billable_action_time(self, accountId):
        #TODO
        #get cloudspaces
        #find machine with earliest creationtime and cloudspaceid in cloudspaces
        #return machine.creationtime
        pass
    
    def _create_empty_billing_statements(self, fromTime, untilTime):
        untilMonthDate = datetime.utcfromtimestamp(untilTime).replace(day=1,minute=0,second=0,microsecond=0)
        untilMonthTime = calendar.timegm(untilMonthDate.timetuple())
        fromMonthDate = datetime.utcfromtimestamp(fromTime).replace(day=1,minute=0,second=0,microsecond=0)
        fromMonthTime = calendar.timegm(fromMonthDate.timetuple())
        billingstatments = []
        while (fromMonthTime < untilMonthTime):
            nextMontTime = self._addMonth(fromMonthTime)
            billingstatement = self.billingenginemodels.bilingstatement.new()
            billingstatement.fromTime = fromMonthTime
            billingstatement.untilTime = nextMonthTime
            billingstatements.append(billingstatement)
            fromMonthTime = nextMonthTime
    
        return billingstatements
    
    def _addMonth(self, timestamp):
        timestampdatetime = datetime.utcfromtimestamp(timestamp)
        monthbeginning = timestampdatetime.replace(day=1,minute=0,second=0,microsecond=0)
        if monthbeginning.month == 12:
            nextmonthbeginning = monthbeginning.replace(year=monthbeginning.year + 1, month=1)
        else:
            nextmonthbeginning = monthbeginning.replace(month=monthbeginning.month+1)
        
        return calendar.timegm(nextmonthbeginning.timetuple())
    
    def createTransactionStaments(self, accountId, **kwargs):
        """
        Generates the missing billing statements and debit transactions for an account
        param:accountId id of the account
        """
        now = int(time.time())
        last_billing_statement = self._get_last_billing_statement(accountId)
        next_billing_statement_time = None
        if not last_transaction_statement is None:
            self._update_usage(last_billing_statement)
            self._save_billing_statement(last_billing_statement)
            next_billing_statement_time = _addMonth(last_billing_statement.time)
        else:
            next_billing_statement_time = self._find_earliest_billable_action_time(accountId)
            
        for billing_statement in self._create_empty_billing_statements(next_billing_statement_time, now):
            self._update_usage(billing_statement)
            self._save_billing_statement(billing_statement)
            
        self.updateBalance(accountId)
        

    def updateBalance(self, accountId, **kwargs):
        """
        Updates the balance for an account given the credit/debit transactions
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
