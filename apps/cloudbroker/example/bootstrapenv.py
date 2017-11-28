from JumpScale import j
import JumpScale.portal
import uuid

cl = j.clients.portal.get('127.0.0.1', 80, '1234')
cl.getActor('cloud','cloudbroker')
cl.getActor('cloudapi','accounts')
cl.getActor('cloudapi','cloudspaces')
cl.getActor('libcloud', 'libvirt')

#create a new stack:
computenodeip = j.console.askString("Enter computenode IP")
stack  = j.apps.cloud.cloudbroker.models.stack.new()
stack.apiUrl = 'qemu+ssh://%s/system' % computenodeip
stack.descr = 'libvirt node'
stack.type = 'LIBVIRT'
stack.name = 'Cloudscaler 02'
j.apps.cloud.cloudbroker.model_stack_set(stack)

# create account
accountid = j.apps.cloudapi.accounts.create('myaccount', ['admin'])

# create cloudspace
j.apps.cloudapi.cloudspaces.create(accountid, 'myspace', ['admin'])

#create resourceprovider
rp = j.apps.libcloud.libvirt.models.resourceprovider.new()
rp.cloudUnitType = 'CU'
rp.id = j.tools.hash.md5_string('qemu+ssh://%s/system' % computenodeip)
rp.capacityAvailable = '500'
j.apps.libcloud.libvirt.model_resourceprovider_set(rp)

#You need to create a image

#A image

image = j.apps.libcloud.libvirt.models.image.new()
image.name = 'testimage'
image.id = str(uuid.uuid4())
image.description = 'testimage'
image.UNCPath = 'base-image.img'
image.size = 10
image.type='ubuntu'
imageid = j.apps.libcloud.libvirt.model_image_set(image)



imagecb = j.apps.cloud.cloudbroker.models.image.new()
imagecb.name = 'testimage'
#this should be the name of the image in the VMStor
imagecb.UNCPath = 'ubuntu-base.img'
imagecb.referenceId = str(imageid)
imagecb.size = 10
imagecb.type='ubuntu'
imagecbid = j.apps.cloud.cloudbroker.model_image_set(imagecb)

rp.images = [imagecbid]
j.apps.libcloud.libvirt.model_resourceprovider_set(rp)


#Create a libcloud_libvirt size
size = j.apps.libcloud.libvirt.models.size.new()
size.disk = 20
size.memory = 1740
size.name = 'SMALL'
size.vcpus = 1
sizeid = j.apps.libcloud.libvirt.model_size_set(size)

size2 = j.apps.libcloud.libvirt.models.size.new()
size2.disk = 40
size2.memory = 3000
size2.name = 'BIG'
size2.vcpus = 2
size2id = j.apps.libcloud.libvirt.model_size_set(size2)

#add iprange to the libvirt config

#j.apps.libcloud.libvirt.addFreeSubnet('192.168.100.0/24')

#A size is also needed in the cloudbroker

sizecb = j.apps.cloud.cloudbroker.models.size.new()
sizecb.name = 'SMALL-CB'
sizecb.referenceId= sizeid
sizecb.memory = 1740
sizecb.vcpus = 1
j.apps.cloud.cloudbroker.model_size_set(sizecb)

sizecb2 = j.apps.cloud.cloudbroker.models.size.new()
sizecb2.name = 'BIG-CB'
sizecb2.referenceId= size2id
sizecb2.memory = 3000
sizecb2.vcpus = 2
j.apps.cloud.cloudbroker.model_size_set(sizecb2)

