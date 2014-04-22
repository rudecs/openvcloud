[actor] @dbtype:mem,osis
    """
    API consumption Actor, this actor is the final api an enduser uses to pay with paypal
    """    

    method:initiatepayment
        """
        Starts a paypal payment flow.
        """
        var:accountId int,,id of the account
        var:reference int,,id of the billingstatement
        result:bool
        
    method:confirmauthorization
    	"""
    	Paypal callback url
    	"""
    	var:paymentId int,,id of the paymentrequest
    	result:string An HTTP "302 Found" response code is given with the url of the confirmation page.
    	
    method:confirmpayment
    	"""
    	Confirm and execute the payment
    	"""
    	var:paymentId int,,id of the paymentrequest
    	result:bool 

