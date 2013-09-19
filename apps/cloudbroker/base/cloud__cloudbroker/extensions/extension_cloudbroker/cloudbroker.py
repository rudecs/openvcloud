from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection


cloudbroker = j.apps.cloud.cloudbroker
ujson = j.db.serializers.ujson

ROUNDROBIN = -1

class Dummy(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

class CloudProvider(object):
    _providers = dict()
    def __init__(self, stackId):
        if stackId not in CloudProvider._providers:
            stack = cloudbroker.model_stack_get(stackId)
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

    def getProviderByResourceProvider(self, providerId):
        if providerId not in CloudBroker._resourceProviderId2StackId:
            provider = cloudbroker.model_resourceprovider_get(providerId)
            CloudBroker._resourceProviderId2StackId[providerId] =  provider['stackId']
        return CloudProvider(CloudBroker._resourceProviderId2StackId[providerId])

    def getProviderByStackId(self, stackId):
        return CloudProvider(stackId)

    def addDiskToMachine(self, machine, disk):
        provider = self.getProvider(machine)
        volume = provider.client.create_volume(disk.sizeMax, disk.name)
        disk.referenceId = volume.id
        provider.client.attach_volume(machine.referenceId, volume)
        return True

    def getIdByReferenceId(self, objname, referenceId):
        queryapi = getattr(cloudbroker, 'model_%s_find' % objname)
        query = {}
        query = {'query': {'term': {'referenceId': referenceId}}, 'fields': ['id']}
        results = queryapi(ujson.dumps(query))['result']
        ids = [res['fields']['id'] for res in results]
        return ids[0] if ids else None


    def getBestProvider(self):
        global ROUNDROBIN
        ROUNDROBIN += 1
        capacityinfo = self.getCapacityInfo()
        if not capacityinfo:
            raise RuntimeError('No Providers available')
        #return sorted(stackdata.items(), key=lambda x: sortByType(x, 'CU'), reverse=True)
        l = len(capacityinfo)
        provider = capacityinfo[ROUNDROBIN % l]
        return provider


    def getCapacityInfo(self):
        # group all units per type
        resourceproviders = cloudbroker.model_resourceprovider_find(ujson.dumps({}))['result']
        resourcesdata = list()
        for resourceprovider in resourceproviders:
            resourceprovider = resourceprovider['_source']
            resourcesdata.append(resourceprovider)
        return resourcesdata

    def stackImportImages(self, stackId):
        provider = CloudProvider(stackId)
        count = 0
        for pimage in provider.client.list_images():
            imageid = self.getIdByReferenceId('image', pimage.name)
            image = cloudbroker.models.image.new()
            if imageid:
                image.dict2obj(cloudbroker.model_image_get(imageid))
            image.name = pimage.name
            image.referenceId = pimage.name
            count += 1
            cloudbroker.model_image_set(image.obj2dict())
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

