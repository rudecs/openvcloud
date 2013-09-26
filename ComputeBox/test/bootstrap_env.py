from JumpScale import j
import JumpScale.portal
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--ip',required=False)
args = parser.parse_args()

cl = j.core.portal.getPortalClient('127.0.0.1', 80, '1234')
cl.getActor('cloud','cloudbroker')
cl.getActor('libcloud', 'libvirt')
cl.getActor('cloudapi','accounts')
cl.getActor('cloudapi','cloudspaces')

#create a new stack:
stack  = j.apps.cloud.cloudbroker.models.stack.new()
stack.apiUrl = 'qemu+ssh:///system'
stack.descr = 'libvirt node'
stack.type = 'LIBVIRT'
stack.name = 'Cloudscaler demo'
j.apps.cloud.cloudbroker.model_stack_set(stack)

#create resourceprovider
rp = j.apps.cloud.cloudbroker.models.resourceprovider.new()
rp.stackId = 1
rp.cloudUnitType = 'CU'
rp.capacityAvailable = '500'
j.apps.cloud.cloudbroker.model_resourceprovider_set(rp)

#An account
j.apps.cloudapi.accounts.create('demo_account', ['admin'])

#A cloudspace
j.apps.cloudapi.cloudspaces.create(1, 'demo_space', ['admin'])

#An image
image = j.apps.libcloud.libvirt.models.image.new()
image.name = 'ubuntu-13.04-server-amd64.iso'
image.description = 'Demo Image'
image.UNCPath = 'base-image.img'
image.size = 10
image.type='ubuntu'
imageid = j.apps.libcloud.libvirt.model_image_set(image)

imagecb = j.apps.cloud.cloudbroker.models.image.new()
imagecb.name = 'ubuntu-13.04-server-amd64.iso'
#this should be the name of the image in the VMStor
imagecb.UNCPath = 'ubuntu-base.img'
imagecb.referenceId = str(imageid)
imagecb.size = 10
imagecb.type='ubuntu'
j.apps.cloud.cloudbroker.model_image_set(imagecb)

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
if not args.ip:
	args.ip = '192.168.100.64/29'
j.apps.libcloud.libvirt.addFreeSubnet(args.ip)

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
