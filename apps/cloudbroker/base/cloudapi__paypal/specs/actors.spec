[actor] @dbtype:mem,osis
    """
    API consumption Actor, this actor is the final api a enduser uses to pay with paypal
    """    

    method:initiatepayment
        """
        Starts a paypal payment flow.
        """
        var:accountId int,,id of the account
        var:reference int,,id of the billingstatement
        result:bool    

