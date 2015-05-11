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
        var:id int,, internal payment id
        var:token str,,token
        var:PayerID str,,PayerID
        result:dict #An HTTP 302 Found response code is given with the url of the confirmation or cancelled page.

    method:confirmvalidation @noauth
        """
        Paypal callback url for the 1$ authorization
        """
        var:id int,, internal payment id
        var:token str,,token
        var:PayerID str,,PayerID
        result:dict #An HTTP 302 Found response code is given with the url of the confirmation or cancelled page.

    method:confirmpayedvalidation @noauth
        """
        Paypal callback url for the 1$ payment, this is in case of a payed validation
        var:id int,, internal payment id
        var:token str,,token
        var:PayerID str,,PayerID
        result dict #An HTTP 302 Found response code is given with the url of the confirmation or cancelled page.
        """
