from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
import random

class Class():
    pass

cloudbroker = j.apps.cloud.cloudbroker

ujson = j.db.serializers.ujson


osiscl = j.core.osis.getClient()

models = Class()
for ns in osiscl.listNamespaceCategories('cloudbroker'):
    models.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
    models.__dict__[ns].find = models.__dict__[ns].search



class Dummy(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

class CloudProvider(object):
    _providers = dict()
    def __init__(self, stackId):
        if stackId not in CloudProvider._providers:
            stack = models.stack.get(stackId)
            providertype = getattr(Provider, stack['type'])
            kwargs = dict()
            if stack['type'] == 'OPENSTACK':
                DriverClass = get_driver(providertype)
                args = [ stack['login'], stack['passwd']]
                kwargs['ex_force_auth_url'] = stack['apiUrl']
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack['login']
                self.client = CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
            if stack['type'] == 'DUMMY':
                DriverClass = get_driver(providertype)
                args = [1,]
                CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
            if stack['type'] == 'LIBVIRT':
                kwargs['id'] = stack['referenceId']
                kwargs['uri'] = stack['apiUrl']
                CloudProvider._providers[stackId] = CSLibvirtNodeDriver(**kwargs)
                cb = CloudBrokerConnection()
                CloudProvider._providers[stackId].set_backend(cb)

        self.client = CloudProvider._providers[stackId]

    def getSize(self, brokersize, firstdisk):
        providersizes = self.client.list_sizes()
        for s in providersizes:
             if s.ram == brokersize['memory'] and firstdisk['sizeMax'] == s.disk:
                return s
        return None

    def getImage(self, imageId):
        iimage = cloudbroker.model_image_get(imageId)
        for image in self.client.list_images():
            if image.id == iimage['referenceId']:
                return image, image




class CloudBroker(object):
    _resourceProviderId2StackId = dict()

    def __init__(self):
        self.Dummy = Dummy

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
        queryapi = getattr(model, 'find')
        query = {}
        query = {'query': {'term': {'referenceId': referenceId}}, 'fields': ['id']}
        queryresult = queryapi(ujson.dumps(query))
        if 'result' in queryresult:
            ids = [res['fields']['id'] for res in queryresult['result']]
        else:
            ids = [res['fields']['id'] for res in queryresult]
        if ids:
            return ids[0]
        else:
            return None
        
    def getBestProvider(self, imageId):
        capacityinfo = self.getCapacityInfo(imageId)
        if not capacityinfo:
            raise RuntimeError('No Providers available')
        #return sorted(stackdata.items(), key=lambda x: sortByType(x, 'CU'), reverse=True)
        l = len(capacityinfo)
        i = random.randint(0, l - 1)
        provider = capacityinfo[i]
        return provider


    def getCapacityInfo(self, imageId):
        # group all units per type
        stacks = models.stack.find(ujson.dumps({"query":{"term": {"images": imageId}}}))
        resourcesdata = list()
        for stack in stacks['result']:
            stack = stack['_source']
            resourcesdata.append(stack)
        return resourcesdata

    def stackImportImages(self, stackId):
        provider = CloudProvider(stackId)
        count = 0
        stack = models.stack.get(stackId)
        stack['images'] = []
        for pimage in provider.client.list_images():
            imageid = self.getIdByReferenceId('image', pimage.id)
            if not imageid:
                image = cloudbroker.models.image.new()
                image.name = pimage.name
                image.referenceId = pimage.id
                image.type = pimage.extra['imagetype']
                image.size = pimage.extra['size']
            else:
                image = models.image.get(imageid)
                image['name'] = pimage.name
                image['referenceId'] = pimage.id
                image['type'] = pimage.extra['imagetype']
                image['size'] = pimage.extra['size']
            count += 1
            imageid = models.image.set(image)
            if not imageid in stack['images']:
                stack['images'].append(imageid)
                models.stack.set(stack)
        return count


    def stackImportSizes(self, stackId):
        provider = CloudProvider(stackId)
        count = 0
        for psize in provider.client.list_sizes():
            sizeid = self.getIdByReferenceId('size', psize.name)
            size = cloudbroker.models.size.new()
            if sizeid:
                size.dict2obj(cloudbroker.model_size_get(sizeid))
            size.CU = psize.ram
            size.name = psize.name
            size.referenceId = psize.name
            size.disk = psize.disk * 1024 #we store in MB
            count += 1
            cloudbroker.model_size_set(size.obj2dict())
        return count

    def getModel(self):
        return models

