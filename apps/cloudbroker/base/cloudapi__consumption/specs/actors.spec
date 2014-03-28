[actor] @dbtype:mem,osis
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details
    """    

    method:get
        """
        Gets detailed consumption for a specific creditTransaction
        The user needs write access rights on the space.    
        """
        var:accountId int,,id of the account
        var:creditTransactionId int,,id of the credit transaction
        result:bool    

