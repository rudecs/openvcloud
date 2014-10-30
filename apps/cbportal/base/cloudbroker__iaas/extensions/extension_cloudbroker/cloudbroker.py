from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
import JumpScale.portal
import JumpScale.grid.osis
import random

class CloudProvider(object):
    providers = dict()
    def __init__(self, stackId):
        cbcl = j.core.osis.getClientForNamespace('cloudbroker')

        stack = cbcl.stack.get(stackId)
        providertype = getattr(Provider, stack.type)
        kwargs = dict()
        if stackId not in CloudProvider.providers:
            if stack.type == 'OPENSTACK':
                DriverClass = get_driver(providertype)
                args = [ stack.login, stack.passwd]
                kwargs['ex_force_auth_url'] = stack.apiUrl
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack.login
                CloudProvider.providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'DUMMY':
                DriverClass = get_driver(providertype)
                args = [1,]
                CloudProvider.providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'LIBVIRT':
                kwargs['id'] = stack.referenceId
                kwargs['uri'] = stack.apiUrl
                kwargs['gid'] = stack.gid
                prov = CSLibvirtNodeDriver(**kwargs)
                cbclient = j.core.portal.getClientByInstance('cloudbroker')
                cb = CloudBrokerConnection(cbclient)
                prov.set_backend(cb)
                CloudProvider.providers[stackId] = prov
        self.cbcl = cbcl
        self.client = CloudProvider.providers[stackId]

    def getSize(self, brokersize, firstdisk):
        providersizes = self.client.list_sizes()
        for s in providersizes:
             if s.ram == brokersize.memory and firstdisk.sizeMax == s.disk:
                return s
        return None

    def getImage(self, imageId):
        iimage = self.cbcl.image.get(imageId)
        for image in self.client.list_images():
            if image.id == iimage.referenceId:
                return image, image
        return None, None


class CloudBroker(object):
    def __init__(self):
        self._actors = None
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')

    @property
    def actors(self):
        if not self._actors:
            cl = j.core.portal.getClientByInstance('cloudbroker')
            self._actors = cl.actors
        return self._actors

    def stackImportImages(self, stackId):
        provider = CloudProvider(stackId)
        if not provider:
            raise RuntimeError('Provider not found')
        count = 0
        stack = provider.cbcl.stack.get(stackId)
        stack.images = list()
        for pimage in provider.client.list_images(): #libvirt/openstack images
            images = provider.cbcl.image.search({'referenceId':pimage.id})[1:]
            if not images:
                image = provider.cbcl.image.new()
                image.name = pimage.name
                image.referenceId = pimage.id
                image.type = pimage.extra['imagetype']
                image.size = pimage.extra['size']
                image.username = pimage.extra['username']
                image.status = pimage.status or 'CREATED'
                image.accountId = 0
            else:
                image = images[0]
                image['name'] = pimage.name
                image['referenceId'] = pimage.id
                image['type'] = pimage.extra['imagetype']
                image['size'] = pimage.extra['size']
                image['username'] = pimage.extra['username']
                image['status'] = pimage.status or 'CREATED'
            count += 1
            imageid = provider.cbcl.image.set(image)[0]
            if not imageid in stack.images:
                stack.images.append(imageid)
                provider.cbcl.stack.set(stack)
        return count

    def getProviderByStackId(self, stackId):
        return CloudProvider(stackId)

    def getBestProvider(self, imageId, excludelist=[]):
        capacityinfo = self.getCapacityInfo(imageId)
        if not capacityinfo:
            raise RuntimeError('No Providers available')
        capacityinfo = [node for node in capacityinfo if node['id'] not in excludelist]
        if not capacityinfo:
            return -1
        #return sorted(stackdata.items(), key=lambda x: sortByType(x, 'CU'), reverse=True)
        l = len(capacityinfo)
        i = random.randint(0, l - 1)
        provider = capacityinfo[i]
        return provider


    def getCapacityInfo(self, imageId):
        # group all units per type
        stacks = self.cbcl.stack.simpleSearch({"images": imageId})
        resourcesdata = list()
        for stack in stacks:
            resourcesdata.append(stack)
        return resourcesdata
