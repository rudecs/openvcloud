from JumpScale import j

class billingengine_billingengine(j.code.classGetBase()):
    """
    Actor for generating negative billing transactions based on cloudusage
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="billingengine"
        self.appname="billingengine"
        #billingengine_billingengine_osis.__init__(self)
    

        pass

    def createTransactionStaments(self, accountId, **kwargs):
        """
        Generates the missing transactions for an account
        param:accountId id of the account
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method createTransactionStaments")
    

    def updateBalance(self, accountId, **kwargs):
        """
        Updates the ballance for an account given the credit/debit transactions
        param:accountId id of the account
        """
        #For now, sum here, as of ES 1.0, can be done there
        query = {'fields': ['time', 'credit', 'status']}
        query['query'] = {'bool':{'must':[{'term': {"accountId": accountId}}],'must_not':[{'term':{'status':'UNCONFIRMED'.lower()}}]}}
        results = self.models.credittransaction.find(ujson.dumps(query))['result']
        history = [res['fields'] for res in results]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
            #TODO: put in processed (but only save after updating the balance
            
        newbalance = self.models.creditbalance.new()
        newbalance.accountId = accountId
        newbalance.time = int(time.time())
        newbalance.credit = balance
        self.models.creditbalance.set(newbalance)
