import requests
import json
#we are using python requests to demonstrate the api
#List images
#List sizes

username = 'enteryourusername'
password = 'enteryourpassword'
#Get a auth key
r = requests.get('http://127.0.0.1/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (username, password))
key = r.json()

imageurl = 'http://127.0.0.1/restmachine/cloudapi/images/list?authkey=%s' % key
sizeurl = 'http://127.0.0.1/restmachine/cloudapi/sizes/list?authkey=%s' % key

#List the accounts on which you have access

accounturl = 'http://127.0.0.1/restmachine/cloudapi/accounts/list?authkey=%s' % key

#List also the cloudspaces you can access
cloudspaceurl = 'http://127.0.0.1/restmachine/cloudapi/cloudspaces/list?authkey=%s' % key

imager = requests.get(imageurl)
sizer = requests.get(sizeurl)
accountr = requests.get(accounturl)

accounts = accountr.json()

cloudspacer = requests.get(cloudspaceurl)

print 'Available Images: %s \n' % imager.json()
print 'Available Sizes %s \n' % sizer.json()
print 'Available Accounts %s \n' % accounts
print 'Available Cloudspaces %s \n' % cloudspacer.json()
