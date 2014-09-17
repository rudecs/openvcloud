import requests
import hashlib, base64, phpserialize

from settings import authenticationparams, WHMCS_API_ENDPOINT


def _call_whmcs_api(requestparams):
    actualrequestparams = dict()
    actualrequestparams.update(requestparams)
    actualrequestparams.update(authenticationparams)
    response = requests.post(WHMCS_API_ENDPOINT, data=actualrequestparams)
    return response

def accept_order(orderId):
    request_params = dict(
                action='acceptorder',
                orderid=orderId,
                sendemail=False
                          )
    response = _call_whmcs_api(request_params)

def add_order(userId, productId, name, cloudbrokerId, location):
    
    request_params = dict(

                action = 'addorder',
                name=name,
                pid = productId,
                clientid = userId,
                billingcycle = 'monthly',
                paymentmethod = 'paypal',
                customfields = base64.b64encode(phpserialize.dumps([cloudbrokerId, name, location])),
                noemail = True,
                skipvalidation= True,
                responsetype = 'json'

                )
    
    response = _call_whmcs_api(request_params)
    return response.json()


def list_orders(orderId = None):
    
    request_params = dict(
                action = 'getorders',
                limitnum = 10000000,
                responsetype = 'json'
                )
    
    if orderId is not None:
        request_params.update({'orderid':orderId})

    response = _call_whmcs_api(request_params)
    if response.ok:
        orders = response.json()
        if orders['numreturned'] > 0:
            return orders['orders']['order']
        return []
    else:
      raise
  
def delete_order(orderId):
    request_params = dict(
                action = 'deleteorder',
                orderid=orderId,
                responsetype = 'json'
                )
    
    response = _call_whmcs_api(request_params)
    return response.ok

def get_order(orderId):
    request_params = dict(
                          )
