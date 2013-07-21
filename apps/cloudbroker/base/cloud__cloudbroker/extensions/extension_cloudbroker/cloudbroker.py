from OpenWizzy import o
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

cloudbroker = o.apps.cloud.cloudbroker
ujson = o.db.serializers.ujson

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
            DriverClass = get_driver(providertype)
            args = [ stack['login'], stack['passwd'] ]
            kwargs = dict()
            if stack['type'] == 'OPENSTACK':
                kwargs['ex_force_auth_url'] = stack['apiUrl']
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack['login']
            CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
        self.client = CloudProvider._providers[stackId]

    def getSize(self, sizeId):
        isize = cloudbroker.model_size_get(sizeId)
        for size in self.client.list_sizes():
            if size.name == isize['referenceId']:
                return isize, size

    def getImage(self, imageId):
        iimage = cloudbroker.model_image_get(imageId)
        for image in self.client.list_images():
            if image.name == iimage['referenceId']:
                return image, image

class CloudBroker(object):

    def createMachine(self, machine):
        resourceprovider = self.getBestProvider(machine)
        provider =  CloudProvider(resourceprovider['stackId'])
        size, psize = provider.getSize(machine.sizeId)
        image, pimage = provider.getImage(machine.imageId)
        machine.cpus = psize.vcpus
        machine.resourceProviderId = resourceprovider['id']
        node = provider.client.create_node(name=machine.name, image=pimage, size=psize)
        machine.referenceId = node.id
        return True


    def getProvider(self, machine):
        if machine.resourceProviderId and machine.referenceId:
            resourceprovider = cloudbroker.model_resourceprovider_get(machine.resourceProviderId)
            return CloudProvider(resourceprovider['stackId'])
        return None


    def deleteMachine(self, machine):
        provider = self.getProvider(machine)
        if provider:
            node = Dummy(id=machine.referenceId)
            provider.client.destroy_node(node)
            return True
        else:
            return False

    def machineAction(self, machine, action):
        provider = self.getProvider(machine)
        if not provider:
            raise RuntimeError("Machine is not initialized")
        node = Dummy(id=machine.referenceId)
        actionname = "%s_node" % action.lower()
        method = getattr(provider.client, actionname, None)
        if not method:
            method = getattr(provider.client, "ex_%s" % actionname, None)
            if not method:
                raise RuntimeError("Action %s is not support on machine %s" % (action, machine.name))
        return method(node)


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


    def getBestProvider(self, machine):
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

