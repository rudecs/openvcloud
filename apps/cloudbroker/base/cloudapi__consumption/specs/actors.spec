[actor] @dbtype:mem,osis
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details
    """    

    method:get
        """
        Gets detailed consumption for a specific creditTransaction.
        """
        var:accountId int,,id of the account
        var:reference int,,id of the billingstatement
        result:bool    

