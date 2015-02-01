from JumpScale import j
import JumpScale.portal

cl = j.clients.portal.get(secret='1234')
cl.getActor('cloud', 'cloudbroker')
#create network
api = j.apps.cloud.cloudbroker
clid = api.cloudSpaceCreate('mycloud', ['admin'])
machineid = api.machineCreate(clid, 'mymachine', 'used for testing', 1)
diskid = api.machineAddDisk(machineid, 'mydisk')
#this might not work as elastiscsearch takes some time to index the data
alsodiskid = api.machineGetDiskId(machineid, 'mydisk')
deletemachine = api.machineDelete(machineid)
