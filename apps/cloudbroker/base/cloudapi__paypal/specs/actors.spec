[actor] @dbtype:mem,osis
    """
    API consumption Actor, this actor is the final api an enduser uses to pay with paypal
    """

    method:initiatepayment
        """
        Starts a paypal payment flow.
        """
        var:accountId int,,id of the account
        var:amount int,,amount of credit to add
        var:currency str,,currency the code of the currency you want to make a payment with (USD currently supported)
        result:dict #A json dict containing the paypal payment confirmation url


    method:confirmauthorization
        """
        Paypal callback url
        """
        var:token str,,token
        var:PayerID str,,PayerID
        result:dict #An HTTP 302 Found response code is given with the url of the confirmation or cancelled page.

    method:confirmpayment
        """
        Confirm and execute the payment
        """
        var:paymentId int,,id of the paymentrequest
        result:bool
