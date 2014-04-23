from JumpScale import j
from cloudbrokerlib import authenticator

class cloudapi_paypal(j.code.classGetBase()):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details

    """
    def __init__(self):
        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass

        self.models = Class()
        for ns in osiscl.listNamespaceCategories('billing'):
            self.models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'billing', ns))
            self.models.__dict__[ns].find = self.models.__dict__[ns].search

        self._te={}
        self.actorname="paypal"
        self.appname="cloudapi"
        #cloudapi_consumption_osis.__init__(self)
        pass



    def confirmauthorization(self, paymentId, **kwargs):
        """
        Paypal callback url
        param:paymentId id of the paymentrequest
        result string
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method confirmauthorization")


    def confirmpayment(self, paymentId, **kwargs):
        """
        Confirm and execute the payment
        param:paymentId id of the paymentrequest
        result bool
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method confirmpayment")


    def initiatepayment(self, accountId, amount, currency, **kwargs):
        """
        Starts a paypal payment flow.
        param:accountId id of the account
        param:amount amount of credit to add
        param:currency currency the code of the currency you want to make a payment with (USD currently supported)
        result dict
        """
        return {'paypalurl':'https://sandbox.paypal.com'}
