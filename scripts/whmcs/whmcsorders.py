import requests
import hashlib

authenticationparams = dict(
                            username = 'api',
                            password = hashlib.md5('kmmlqwkerjoi324mmkkjhapl02bc').hexdigest(),
                            accesskey = 'mmqewnlzklpo89ka234mkm2o1287kmmzbpldgej3'
                            )

def _call_whmcs_api(requestparams):
    actualrequestparams = dict()
    actualrequestparams.update(requestparams)
    actualrequestparams.update(authenticationparams)
    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=actualrequestparams)
    return response

def add_order(userId, productId, cloudbrokerId):
    
    request_params = dict(

                action = 'addorder',
                pid = productId,
                clientid = userId,
                billingcycle = 'monthly',
                paymentmethod = 'paypal',
                customfields = [cloudbrokerId, creationTime],
                noemail = True,
                skipvalidation= True

                )
    
    response = _call_whmcs_api(create_user_request_params)
    return response.ok


def list_orders():
    
    request_params = dict(
                action = 'getorders',
                limitnum = 10000000,
                responsetype = 'json'
                )

    response = _call_whmcs_api(request_params)
    if response.ok:
        orders = response.json()
        if orders['numreturned'] > 0:
            return orders['orders']
        return []
    else:
      raise
  
def delete_order(orderId):
    request_params = dict(
                action = 'deleteorder',
                orderid=orderId,
                responsetype = 'json'
                )
    
    response = _call_whmcs_api(delete_users_request_params)
    return response.ok
