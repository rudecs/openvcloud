from JumpScale import j

class cloudapi_consumption(j.code.classGetBase()):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="consumption"
        self.appname="cloudapi"
        #cloudapi_consumption_osis.__init__(self)
    

        pass

    def get(self, accountId, creditTransactionId, **kwargs):
        """
        Gets detailed consumption for a specific creditTransaction.
        param:accountId id of the account
        param:creditTransactionId id of the credit transaction
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")
    
