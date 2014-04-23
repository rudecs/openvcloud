from JumpScale import j
from cloudbrokerlib import authenticator
import requests
from requests.auth import HTTPBasicAuth
import ujson

class cloudapi_paypal(j.code.classGetBase()):
    """
    API consumption Actor, this actor is the final api a enduser uses to get consumption details

    """
    def __init__(self):

        self.paypal_user = 'AR3m7BDSytnZsBY_dSQr23VJ1E_63LQrHr7jZ6OIchco3RmoFjhNRDhLuuUT'
        self.paypal_secret = 'EKcPPRDv9IBNQ6g0io06kO1GvSZtWRA0WdM3BGOMRp4qqSRfNiZ4eqLaq8g1'
        self.paypal_url = 'https://api.sandbox.paypal.com'


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


    def _get_paypal_token(self):

        tokenurl = '%s/v1/oauth2/token' % self.paypal_url
        headers = {'Accept': 'application/json'}
        payload = {'grant_type':'client_credentials'}
        paypalresponse = requests.post(tokenurl,headers=headers,data=payload,auth=HTTPBasicAuth(self.paypal_user, self.paypal_secret))
        if paypalresponse.status_code is not 200:
            #TODO raise error
            pass
        paypalresponsedata = paypalresponse.json()
        access_token = paypalresponsedata['access_token']
        #TODO: cache the token
        return access_token

    def confirmauthorization(self, token, PayerID, **kwargs):
        """
        Paypal callback url
        param:token
        param:PayerID
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
        access_token = self._get_access_token()

        paymenturl = '%s/v1/payments/payment' % self.paypal_url
        payload = {
                   "intent":"sale",
                   "redirect_urls":{
                                    "return_url":"https://test1.mothership1.com/restmachine/cloudapi/paypal",
                                    "cancel_url":"https://test1.mothership1.com/restmachine/cloudapi/paypal"
                                   },
                   "payer":{
                            "payment_method":"paypal"
                           },
                   "transactions":[
                                   {
                                    "amount":{
                                              "total":amount,
                                              "currency":"USD"
                                             }
                                   }
                                  ]
                  }

        headers = {'content-type': 'application/json', 'Authorization': 'Bearer %s' % access_token}
        paypalresponse = requests.post(paymenturl, headers=headers,data=ujson.dumps(payload))
        if paypalresponse.status_code is not 201:
             #TODO raise error
             pass
        paypalresponsedata = paypalresponse.json()
        approval_url = next((link['href'] for link in paypalresponsedata['links'] if link['rel'] == 'approval_url'), None)
        return {'paypalurl':approval_url}
