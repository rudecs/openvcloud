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
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method updateBalance")
    
