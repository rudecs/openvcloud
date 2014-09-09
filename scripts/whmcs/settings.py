import hashlib

authenticationparams = dict(
                            username = 'api',
                            password = hashlib.md5('kmmlqwkerjoi324mmkkjhapl02bc').hexdigest(),
                            accesskey = 'mmqewnlzklpo89ka234mkm2o1287kmmzbpldgej3'
                            )

WHMCS_API_ENDPOINT = 'http://whmcsdev/whmcs/includes/api.php'

CLOUDSPACE_PRODUCT_ID = 34