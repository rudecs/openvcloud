from JumpScale import j

cl = j.core.appserver6.getAppserverClient(secret='1234')
cl.getActor('cloud', 'cloudbroker')
api = j.apps.cloud.cloudbroker
#create stack

stack = api.models.stack.new()
stack.name = 'Open Stack'
stack.type = 'OPENSTACK'
stack.login = 'admin'
stack.passwd = 'rooter'
stack.apiUrl = 'http://10.101.158.1:5000/v2.0'
stackid = api.model_stack_set(stack.obj2dict())

resourceprovider = api.models.resourceprovider.new()
resourceprovider.capacityAvailable = 100
resourceprovider.cloudUnitType = 'CU'
resourceprovider.stackId = stackid
resourceprovider.referenceId = None #OpenStack does capacity management for us meaning we only configure one provider withouth reference
resourceproviderid = api.model_resourceprovider_set(resourceprovider.obj2dict())


stack = api.models.stack.new()
stack.name = 'CloudFrames Stack 1'
stack.type = 'CLOUDFRAMES'
stack.login = 'admin'
stack.passwd = 'admin'
stack.apiUrl = 'http://10.100.99.1'
stackid = api.model_stack_set(stack.obj2dict())
#add at least one resourceprovider
resourceprovider = api.models.resourceprovider.new()
resourceprovider.capacityAvailable = 100
resourceprovider.cloudUnitType = 'CU'
resourceprovider.stackId = stackid
resourceprovider.referenceId = '60b9df52-1542-4234-82b0-98f832618577' # in case of cloudframes this is the pmachineguid, can be empty if cloudframes exists out of single node
resourceproviderid = api.model_resourceprovider_set(resourceprovider.obj2dict())

