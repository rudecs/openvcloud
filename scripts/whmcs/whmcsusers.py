import requests
import hashlib



authenticationparams = dict(

                            username = 'api',

                            password = hashlib.md5('kmmlqwkerjoi324mmkkjhapl02bc').hexdigest(),

                            accesskey = 'mmqewnlzklpo89ka234mkm2o1287kmmzbpldgej3'

                            )

def create_user(name, company, emails, password, companyurl, displayname, creationTime):
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
    create_user_request_params.update(authenticationparams)
    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=create_user_request_params)
    return response.ok


def update_user():
    print

def list_users():
    result_users = {}
    list_users_request_params = dict(
                action = 'getclients',
                limitnum = 10000000,
                responsetype = 'json'
                )
    list_users_request_params.update(authenticationparams)
    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=list_users_request_params)
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
    delete_users_request_params.update(authenticationparams)
    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=delete_users_request_params)
    return response.ok


def add_credit(userid, description, amount):
    add_credit_request_params = dict(
                action = 'addcredit',
                clientid=userid,
                description=description,
                amount=amount,
                responsetype = 'json'
                )
    add_credit_request_params.update(authenticationparams)
    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=add_credit_request_params)
    return response.ok


def add_debit(userid):
    pass


