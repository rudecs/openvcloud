import requests
import json
import time
#we are using python requests to demonstrate the api
#Create a single machine

#Change those values!
username = 'hendrik'
password = 'test'
cloudspaceId = 10
sizeId = 1
imageId = 19
name = 'script_example' + str(time.time())
#Get a auth key
r = requests.get('http://127.0.0.1/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (username, password))
key = r.json()

create_url = 'http://127.0.0.1/restmachine/cloudapi/machines/create?cloudspaceId=%s&sizeId=%s&imageId=%s&disksize=10&name=%s&authkey=%s' % (cloudspaceId, sizeId, imageId, name, key)

machine = requests.get(create_url)

print 'New machine created with id %s' % machine.json()