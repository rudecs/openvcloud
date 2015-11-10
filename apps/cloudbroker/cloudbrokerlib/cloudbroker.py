from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthPassword
from JumpScale.portal.portal import exceptions
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.compute.drivers.openstack_driver import OpenStackNodeDriver
from cloudbrokerlib import enums
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
from billingenginelib import pricing
from billingenginelib import account as accountbilling
import random
import time
import string

ujson = j.db.serializers.ujson
models = j.clients.osis.getNamespace('cloudbroker')

def removeConfusingChars(input):
    return input.replace('0', '').replace('O', '').replace('l', '').replace('I', '')

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
        self.machine = Machine(self)

    @property
    def actors(self):
        if not self._actors:
            cl = j.clients.portal.getByInstance('cloudbroker')
            self._actors = cl.actors
        return self._actors

    def getProviderByStackId(self, stackId):
        return CloudProvider(stackId)

    def addDiskToMachine(self, machine, disk):
        return True

    def getProviderByGID(self, gid):
        stacks = models.stack.search({'gid': gid, 'status': 'ENABLED'})[1:]
        if stacks:
            return self.getProviderByStackId(stacks[0]['id'])
        raise ValueError('No provider available on grid %s' % gid)

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
                if set(cb_size['disks']) == set(psizes[record]):
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

class Machine(object):
    def __init__(self, cb):
        self.cb = cb
        self.acl = j.clients.agentcontroller.get()
        self._pricing = pricing.pricing()
        self._accountbilling = accountbilling.account()

    def cleanup(self, machine):
        for diskid in machine.disks:
            models.disk.delete(diskid)
        models.vmachine.delete(machine.id)

    def validateCreate(self, cloudspace, name, sizeId, imageId, disksize, minimum_days_of_credit_required):
        if not self._assertName(cloudspace.id, name):
            raise exceptions.Conflict('Selected name already exists')
        if not disksize:
            raise exceptions.BadRequest("Invalid disksize %s" % disksize)

        if cloudspace.status == 'DESTROYED':
            raise exceptions.BadRequest('Can not create machine on destroyed Cloud Space')

        sizeId = int(sizeId)
        imageId = int(imageId)
        #Check if there is enough credit
        accountId = cloudspace.accountId
        available_credit = self._accountbilling.getCreditBalance(accountId)
        burnrate = self._pricing.get_burn_rate(accountId)['hourlyCost']
        hourly_price_new_machine = self._pricing.get_price_per_hour(imageId, sizeId, disksize)
        new_burnrate = burnrate + hourly_price_new_machine
        if available_credit < (new_burnrate * 24 * minimum_days_of_credit_required):
            raise exceptions.Conflict('Not enough credit for this machine to run for %i days' % minimum_days_of_credit_required)

    def _assertName(self, cloudspaceId, name, **kwargs):
        results = models.vmachine.search({'cloudspaceId': cloudspaceId, 'name': name, 'status': {'$nin': ['DESTROYED', 'ERROR']}})[1:]
        return False if results else True

    def createModel(self, name, description, cloudspace, imageId, sizeId, disksize, datadisks):
        datadisks = datadisks or []

        #create a public ip and virtual firewall on the cloudspace if needed
        if cloudspace.status != 'DEPLOYED':
            args = {'cloudspaceId': cloudspace.id}
            self.acl.executeJumpscript('cloudscalers', 'cloudbroker_deploycloudspace', args=args, nid=j.application.whoAmI.nid, wait=False)

        machine = models.vmachine.new()
        image = models.image.get(imageId)
        machine.cloudspaceId = cloudspace.id
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId
        machine.creationTime = int(time.time())

        def addDisk(order, size, type, name=None):
            disk = models.disk.new()
            disk.name = name or 'Disk nr %s' % order
            disk.descr = 'Machine disk of type %s' % type
            disk.sizeMax = size
            disk.accountId = cloudspace.accountId
            disk.gid = cloudspace.gid
            disk.order = order
            disk.type = type
            diskid = models.disk.set(disk)[0]
            machine.disks.append(diskid)
            return diskid

        addDisk(-1, disksize, 'B', 'Boot disk')
        diskinfo = []
        for order, datadisksize in enumerate(datadisks):
            diskid = addDisk(order, datadisksize, 'D')
            diskinfo.append((diskid, datadisksize))

        account = machine.new_account()
        if image.type == 'Custom Templates':
            account.login = 'Custom login'
            account.password = 'Custom password'
        else:
            if hasattr(image, 'username') and image.username:
                account.login = image.username
            else:
                account.login = 'cloudscalers'
            length = 6
            chars = removeConfusingChars(string.letters + string.digits)
            letters = [removeConfusingChars(string.ascii_lowercase), removeConfusingChars(string.ascii_uppercase)]
            passwd = ''.join(random.choice(chars) for _ in xrange(length))
            passwd = passwd + random.choice(string.digits) + random.choice(letters[0]) + random.choice(letters[1])
            account.password = passwd
        auth = NodeAuthPassword(account.password)
        machine.id = models.vmachine.set(machine)[0]
        return machine, auth, diskinfo

    def updateMachineFromNode(self, machine, node, stackId, psize):
        machine.referenceId = node.id
        machine.referenceSizeId = psize.id
        machine.stackId = stackId
        machine.status = enums.MachineStatus.RUNNING
        machine.hostName = node.name
        if 'ifaces' in node.extra:
            for iface in node.extra['ifaces']:
                for nic in machine.nics:
                    if nic.macaddress == iface.mac:
                        break
                else:
                    nic = machine.new_nic()
                    nic.macAddress = iface.mac
                    nic.deviceName = iface.target
                    nic.type = iface.type
                    nic.ipAddress = 'Undefined'
        else:
            for ipaddress in node.public_ips:
                nic = machine.new_nic()
                nic.ipAddress = ipaddress
        models.vmachine.set(machine)

        for order, diskid in enumerate(machine.disks):
            disk = models.disk.get(diskid)
            disk.stackId = stackId
            disk.referenceId = node.extra['volumes'][order].id
            models.disk.set(disk)

        cloudspace = models.cloudspace.get(machine.cloudspaceId)
        providerstacks = set(cloudspace.resourceProviderStacks)
        providerstacks.add(stackId)
        cloudspace.resourceProviderStacks = list(providerstacks)
        models.cloudspace.set(cloudspace)

    def create(self, machine, auth, cloudspace, diskinfo, imageId, stackId):
        try:
            if not stackId:
                stack = self.cb.getBestProvider(cloudspace.gid, imageId)
                if stack == -1:
                    self.cleanup(machine)
                    raise exceptions.ServiceUnavailable('Not enough resources available to provision the requested machine')
                stackId = stack['id']
            provider = self.cb.getProviderByStackId(stackId)
            psize = self.getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            machine.cpus = psize.vcpus if hasattr(psize, 'vcpus') else None
            name = 'vm-%s' % machine.id
        except:
            self.cleanup(machine)
            raise
        try:
            node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth, networkid=cloudspace.networkId, datadisks=diskinfo)
        except:
            machine.status = 'ERROR'
            models.vmachine.set(machine)
            raise
        self.updateMachineFromNode(machine, node, stackId, psize)
        tags = str(machine.id)
        j.logger.log('Created', category='machine.history.ui', tags=tags)
        return machine.id

    def getSize(self, provider, machine):
        brokersize = models.size.get(machine.sizeId)
        firstdisk = models.disk.get(machine.disks[0])
        return provider.getSize(brokersize, firstdisk)

