from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
import random

ujson = j.db.serializers.ujson
models = j.core.osis.getClientForNamespace('cloudbroker')

class Dummy(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

class CloudProvider(object):
    _providers = dict()
    def __init__(self, stackId):
        if stackId not in CloudProvider._providers:
            stack = models.stack.get(stackId)
            providertype = getattr(Provider, stack.type)
            kwargs = dict()
            if stack.type == 'OPENSTACK':
                DriverClass = get_driver(providertype)
                args = [ stack.login, stack.passwd]
                kwargs['ex_force_auth_url'] = stack.apiUrl
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack.login
                self.client = CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'DUMMY':
                DriverClass = get_driver(providertype)
                args = [1,]
                CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'LIBVIRT':
                kwargs['id'] = stack.referenceId
                kwargs['uri'] = stack.apiUrl
                kwargs['gid'] = stack.gid
                driver = CSLibvirtNodeDriver(**kwargs)
                client = None
                if not j.apps.actorsloader.existsActor('libvirt', 'libcloud'):
                    client = j.core.portal.getClientByInstance('cloudbroker')
                cb = CloudBrokerConnection(client)
                driver.set_backend(cb)
                CloudProvider._providers[stackId] = driver

        self.client = CloudProvider._providers[stackId]

    def getSize(self, brokersize, firstdisk):
        providersizes = self.client.list_sizes()
        for s in providersizes:
             if s.ram == brokersize.memory and firstdisk.sizeMax == s.disk:
                return s
        return None

    def getImage(self, imageId):
        iimage = models.image.get(imageId)
        for image in self.client.list_images():
            if image.id == iimage.referenceId:
                return image, image
        return None, None

class CloudBroker(object):
    _resourceProviderId2StackId = dict()

    def __init__(self):
        self.Dummy = Dummy
        self._actors = None

    @property
    def actors(self):
        if not self._actors:
            cl = j.core.portal.getClientByInstance('cloudbroker')
            self._actors = cl.actors
        return self._actors

    def getProviderByStackId(self, stackId):
        return CloudProvider(stackId)

    def addDiskToMachine(self, machine, disk):
        provider = self.getProvider(machine)
        volume = provider.client.create_volume(disk.sizeMax, disk.name)
        disk.referenceId = volume.id
        provider.client.attach_volume(machine.referenceId, volume)
        return True

    def getIdByReferenceId(self, objname, referenceId):
        model = getattr(models, '%s' % objname)
        queryapi = getattr(model, 'search')
        query = {'referenceId': referenceId}
        ids = queryapi(query)[1:]
        if ids:
            return ids[0]['id']
        else:
            return None

    def getBestProvider(self, gid, imageId, excludelist=[]):
        capacityinfo = self.getCapacityInfo(gid, imageId)
        if not capacityinfo:
            return -1
        capacityinfo = [node for node in capacityinfo if node['id'] not in excludelist]
        if not capacityinfo:
            return -1
        #return sorted(stackdata.items(), key=lambda x: sortByType(x, 'CU'), reverse=True)
        l = len(capacityinfo)
        i = random.randint(0, l - 1)
        provider = capacityinfo[i]
        return provider

    def getCapacityInfo(self, gid, imageId):
        # group all units per type
        resourcesdata = list()
        stacks = models.stack.search({"images": imageId, 'gid': gid})[1:]
        for stack in stacks:
            if stack.get('status', 'ENABLED') == 'ENABLED':
                resourcesdata.append(stack)
        return resourcesdata

    def stackImportImages(self, stackId):
        provider = CloudProvider(stackId)
        if not provider:
            raise RuntimeError('Provider not found')
        count = 0
        stack = models.stack.get(stackId)
        stack.images = list()
        for pimage in provider.client.list_images(): #libvirt/openstack images
            images = models.image.search({'referenceId':pimage.id})[1:]
            if not images:
                image = models.image.new()
                image.name = pimage.name
                image.referenceId = pimage.id
                image.type = pimage.extra.get('imagetype', 'Unknown')
                image.size = pimage.extra.get('size', 0)
                image.username = pimage.extra.get('username', 'cloudscalers')
                image.status = getattr(pimage, 'status', 'CREATED') or 'CREATED'
                image.accountId = 0
            else:
                image = images[0]
                image['name'] = pimage.name
                image['referenceId'] = pimage.id
                image['type'] = pimage.extra.get('imagetype', 'Unknown')
                image['size'] = pimage.extra.get('size', 0)
                image['username'] = pimage.extra.get('username', 'cloudscalers')
                image['status'] = getattr(pimage, 'status', 'CREATED') or 'CREATED'
            count += 1
            imageid = models.image.set(image)[0]
            if not imageid in stack.images:
                stack.images.append(imageid)
                models.stack.set(stack)
        return count
