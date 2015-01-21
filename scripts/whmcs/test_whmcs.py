import requests
import hashlib



authenticationparams = dict(

                            username = 'api',

                            password = hashlib.md5('kmmlqwkerjoi324mmkkjhapl02bc').hexdigest(),

                            accesskey = 'mmqewnlzklpo89ka234mkm2o1287kmmzbpldgej3'

                            )



def createClient():

    

    params = dict(

                  action = 'addclient', 

                  responsetype = 'json',

                  firstname = "Test",

                  lastname = "User",

                  companyname = "WHMCS",

                  email = "demo@whmcs.com",

                  password2 = "demo",

                  country = "US",

                  currency = "1"

                  )

    params.update(authenticationparams)

    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=params)

    print response.read

    

if __name__ == '__main__':

    params = {}

    params['action'] = 'getclients'

    params['responsetype'] = 'json'

    

    params.update(authenticationparams)

    response = requests.post('http://whmcsdev/whmcs/includes/api.php',data=params)

    

    
    import ipdb
    ipdb.set_trace()
    print response

    

    #createClient()

