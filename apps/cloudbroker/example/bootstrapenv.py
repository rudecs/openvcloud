from JumpScale import j
import JumpScale.portal

cl = j.core.portal.getPortalClient('127.0.0.1', 80, '1234')
cl.getActor('cloud','cloudbroker')

#create a new stack:
computenodeip = j.console.askString("Enter computenode IP")
stack  = j.apps.cloud.cloudbroker.models.stack.new()
stack.apiUrl = 'qemu+ssh://%s/system' % computenodeip
stack.descr = 'libvirt node'
stack.type = 'LIBVIRT'
stack.name = 'Cloudscaler 02'
j.apps.cloud.cloudbroker.model_stack_set(stack)

#create resourceprovider
rp = j.apps.cloud.cloudbroker.models.resourceprovider.new()
rp.stackId = 1
rp.cloudUnitType = 'CU'
rp.capacityAvailable = '500'
j.apps.cloud.cloudbroker.model_resourceprovider_set(rp)

#You need to create a image

#A image

image = j.apps.cloud.cloudbroker.models.image.new()
image.name = 'ubuntu-2'
#this should be the name of the image in the VMStor
image.UNCPath = 'ubuntu-base.img'
image.referenceId = 'ubuntu-2'
image.size = 10
image.type='ubuntu'
j.apps.cloud.cloudbroker.model_image_set(image)

#A size is also needed:

size = j.apps.cloud.cloudbroker.models.size.new()
size.name = 'big'
size.referenceId='big'
size.CU = '1'
size.disks = '20'
j.apps.cloud.cloudbroker.model_size_set(size)

