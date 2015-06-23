from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.compute.drivers.openstack_driver import OpenStackNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
import random

ujson = j.db.serializers.ujson
models = j.clients.osis.getNamespace('cloudbroker')


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
                args = [stack.login, stack.passwd]
                kwargs['ex_force_auth_url'] = stack.apiUrl
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack.login
                driver = OpenStackNodeDriver(*args, **kwargs)
                CloudProvider._providers[stackId] = driver
            if stack.type == 'DUMMY':
                DriverClass = get_driver(providertype)
                args = [1, ]
                CloudProvider._providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'LIBVIRT':
                kwargs['id'] = stack.referenceId
                kwargs['uri'] = stack.apiUrl
                kwargs['gid'] = stack.gid
                driver = CSLibvirtNodeDriver(**kwargs)
                client = None
                if 'libcloud__libvirt' not in j.apps.system.contentmanager.getActors():
                    client = j.clients.portal.getByInstance('cloudbroker')
                cb = CloudBrokerConnection(client)
                driver.set_backend(cb)
                CloudProvider._providers[stackId] = driver

        self.client = CloudProvider._providers[stackId]

    def getSize(self, brokersize, firstdisk):
        providersizes = self.client.list_sizes()
        for s in providersizes:
            if s.ram == brokersize.memory and firstdisk.sizeMax == s.disk and s.extra['vcpus'] == brokersize.vcpus:
                return s
        return None

    def getImage(self, imageId):
        iimage = models.image.get(imageId)
        for image in self.client.ex_list_images():
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
            cl = j.clients.portal.getByInstance('cloudbroker')
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
        # return sorted(stackdata.items(), key=lambda x: sortByType(x, 'CU'), reverse=True)
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

    def stackImportSizes(self, stackId):
        """
        Import disk sizes from a provider

        :param      stackId: Stack ID
        :type       id: ``int``

        :rtype: ``int``
        """
        provider = CloudProvider(stackId)
        if not provider:
            raise RuntimeError('Provider not found')

        stack = models.stack.get(stackId)
        gridId = stack.gid
        cb_sizes = models.size.search({})[1:]  # cloudbroker sizes
        psizes = {}  # provider sizes

        # provider sizes formated as {(memory, cpu):[disks]}. i.e {(2048, 2):[10, 20, 30]}
        for s in provider.client.list_sizes():
            md = (s.ram, s.extra['vcpus'])
            psizes[md] = psizes.get(md, []) + [s.disk]

        for cb_size in cb_sizes:
            record = (cb_size['memory'], cb_size['vcpus'])
            if record not in psizes:  # obsolete sizes
                if gridId in cb_size['gids']:
                    cb_size['gids'].remove(gridId)  # remove gid from obsolete size
                    if not cb_size['gids']:
                        models.size.delete(cb_size['id'])  # delete obsolete size if having no gids
                    else:
                        models.size.set(cb_size)  # update obsolete size [Save without the gridId of the stack]
            else:
                # Update existing sizes (disks and gids)
                if cb_size['disks'] == psizes[record]:
                    if gridId not in cb_size['gids']:
                        cb_size['gids'].append(gridId)
                        models.size.set(cb_size)
                    psizes.pop(record)  # remove from dict
        # add new
        for k, v in psizes.iteritems():
            s = models.size.new()
            s.memory = k[0]
            s.vcpus = k[1]
            s.gids = [gridId]
            s.disks = v
            models.size.set(s)

        # Return length of newly added sizes
        return len(psizes)

    def stackImportImages(self, stackId):
        """
        Sync Provider images [Deletes obsolete images that are deleted from provider side/Add new ones]
        """
        provider = CloudProvider(stackId)
        if not provider:
            raise RuntimeError('Provider not found')

        pname = provider.client.name.lower()
        stack = models.stack.get(stackId)
        stack.images = list()

        pimages = {}
        for p in provider.client.ex_list_images():
            pimages[p.id] = p
        pimages_ids = set(pimages.keys())

        images_current = models.image.search({'provider_name': pname})[1:]
        images_current_ids = set([p['referenceId'] for p in images_current])

        new_images_ids = pimages_ids - images_current_ids
        updated_images_ids = pimages_ids & images_current_ids

        # Add new Images
        for id in new_images_ids:
            pimage = pimages[id]
            image = models.image.new()
            image.provider_name = pname
            image.name = pimage.name
            image.referenceId = pimage.id
            image.type = pimage.extra.get('imagetype', 'Unknown')
            image.size = pimage.extra.get('size', 0)
            image.username = pimage.extra.get('username', 'cloudscalers')
            image.status = getattr(pimage, 'status', 'CREATED') or 'CREATED'
            image.accountId = 0

            imageid = models.image.set(image)[0]
            stack.images.append(imageid)

        # Update current images
        for image in models.image.search({'referenceId': {'$in': list(updated_images_ids)}})[1:]:
            pimage = pimages[image['referenceId']]
            image['name'] = pimage.name
            image['type'] = pimage.extra.get('imagetype', 'Unknown')
            image['size'] = pimage.extra.get('size', 0)
            image['username'] = pimage.extra.get('username', 'cloudscalers')
            image['status'] = getattr(pimage, 'status', 'CREATED') or 'CREATED'
            image['provider_name'] = pname

            imageid = models.image.set(image)[0]
            stack.images.append(imageid)

        models.stack.set(stack)
        return len(new_images_ids)
