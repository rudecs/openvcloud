import requests
import hashlib
from JumpScale import j
from JumpScale import grid



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














cb = j.core.osis.getClientForNamespace('cloudbroker')
system = j.core.osis.getClientForNamespace('system')



accounts = cb.account.list()
users = list_users()
for user in users:
    delete_user(users[user]['id'])
for i in accounts:
  acc = cb.account.get(i)
  linked_users = system.user.simpleSearch({'id':acc.name})
  if len(linked_users) != 1:
    continue
  linked_user = linked_users[0]
  linked_groups = system.group.simpleSearch({'id':acc.name})
  if len(linked_groups) != 1:
    continue
  print linked_user
  password = ''
  if 'passwd' in linked_user:
      password =linked_user['passwd']
  if not acc.name in users.keys():
      create_user(acc.name, acc.company, linked_user['emails'], password, acc.companyurl, acc.displayname, acc.creationTime)
