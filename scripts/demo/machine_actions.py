import requests
import json
import time
#we are using python requests to demonstrate the api
#Resume pause a machine

#Change those values!
username = 'enteryourusername'
password = 'enteryourpassword'
machineid = 661
#Get a auth key
r = requests.get('http://127.0.0.1/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (username, password))
key = r.json()

pause_url = 'http://127.0.0.1/restmachine/cloudapi/machines/pause?machineId=%s&authkey=%s' % (machineid, key)
resume_url = 'http://127.0.0.1/restmachine/cloudapi/machines/resume?machineId=%s&authkey=%s' % (machineid, key)
get_url = 'http://127.0.0.1/restmachine/cloudapi/machines/get?machineId=%s&authkey=%s' % (machineid, key)
#first pause the machine
machine = requests.get(pause_url)

#get the status of the machine
machine = requests.get(get_url)
print 'Machine status with id %s is %s' % (machineid, machine.json()['status'])

time.sleep(5)
#resume after 5s


machine = requests.get(resume_url)
machine =requests.get(get_url)
print 'Machine status with id %s is %s' % (machineid, machine.json()['status'])


