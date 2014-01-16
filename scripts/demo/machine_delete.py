import requests
import json
import time
#we are using python requests to demonstrate the api
#Delete a machine

#Change those values!
username = 'enteryourusername'
password = 'enteryourpassword'
machineid = 661
#Get a auth key
r = requests.get('http://127.0.0.1/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (username, password))
key = r.json()

delete_url = 'http://127.0.0.1/restmachine/cloudapi/machines/delete?machineId=%s&authkey=%s' % (machineid, key)

#first pause the machine
machine = requests.get(delete_url)
print 'Machine %s successfull deleted' % machineid
