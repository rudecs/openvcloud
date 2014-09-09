import requests
import hashlib
from settings import authenticationparams, WHMCS_API_ENDPOINT


def _call_whmcs_api(requestparams):
    actualrequestparams = dict()
    actualrequestparams.update(requestparams)
    actualrequestparams.update(authenticationparams)
    response = requests.post(WHMCS_API_ENDPOINT, data=actualrequestparams)
    return response

def create_user(name, company, emails, password, companyurl, displayname, creationTime):
    print 'Creating %s' % name
    create_user_request_params = dict(

                action = 'addclient',
                responsetype = 'json',
                firstname = name,
                lastname = "",
                companyname = company,
                email = emails,
                password2 = password,
                country = "unknown",
                currency = "1",
                customfields = [companyurl, displayname, creationTime],
                noemail = True,
                skipvalidation= True

                )
    
    response = _call_whmcs_api(create_user_request_params)
    return response.ok


def update_user(name, company, emails, password, companyurl, displayname, creationTime):
    print 'Updating %s' % name
    user_request_params = dict(

                action = 'updateclient',
                responsetype = 'json',
                firstname = name,
                companyname = company,
                email = emails,
                password2 = password,
                customfields = [companyurl, displayname, creationTime],
                noemail = True,
                skipvalidation= True

                )
    
    response = _call_whmcs_api(user_request_params)
    return response.ok

def list_users():
    result_users = {}
    list_users_request_params = dict(
                action = 'getclients',
                limitnum = 10000000,
                responsetype = 'json'
                )

    response = _call_whmcs_api(list_users_request_params)
    if response.ok:
        users = response.json()
        if users['numreturned'] > 0:
            for u in users['clients']['client']:
                result_users[u['firstname']] = u
        return result_users
    else:
      raise


def delete_user(userid):
    delete_users_request_params = dict(
                action = 'deleteclient',
                clientid=userid,
                responsetype = 'json'
                )
    
    response = _call_whmcs_api(delete_users_request_params)
    return response.ok


def add_credit(userid, description, amount):
    add_credit_request_params = dict(
                action = 'addcredit',
                clientid=userid,
                description=description,
                amount=amount,
                responsetype = 'json'
                )
    response = _call_whmcs_api(add_credit_request_params)
    return response.ok


def add_debit(userid):
    pass


