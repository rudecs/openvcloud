from JumpScale import j

cl = j.core.appserver6.getAppserverClient(secret='mysecret')
cl.getActor('cloudapi', 'account')
cl.getActor('cloudapi', 'cloudspace')
cl.getActor('cloudapi', 'machine')
cl.getActor('cloudapi', 'sizes')
cl.getActor('cloudapi', 'images')
api = j.apps.cloudapi

#create an account
accountId = api.account.create('myCompany', ['admin'])
#create network with max 20GB memory and max 2TB disk space
cloudspaceId = api.cloudspace.create(accountId, 'myspace', ['admin'], maxMemoryCapacity=20480, maxDiskCapacity=2048)
sizeId = api.sizes.list()[0]
imageId = api.images.list()[0]
machineId = api.machine.create(cloudspaceId, 'mymachine', 'my description', sizeId, imageId)
