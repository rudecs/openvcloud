from JumpScale import j
from JumpScale.portal.portal import exceptions
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor
from CloudscalerLibcloud.compute.drivers.libvirt_driver import OpenvStorageVolume, OpenvStorageISO, PhysicalVolume

MIN_IOPS = 80

class cloudapi_disks(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """

    def __init__(self):
        super(cloudapi_disks, self).__init__()
        self.osisclient = j.core.portal.active.osis
        self.osis_logs = j.clients.osis.getCategory(self.osisclient, "system", "log")
        self._minimum_days_of_credit_required = float(self.hrd.get(
            "instance.openvcloud.cloudbroker.creditcheck.daysofcreditrequired"))

    def getStorageVolume(self, disk, provider, node=None):
        if not isinstance(disk, dict):
            disk = disk.dump()

        volumeclass = OpenvStorageVolume
        name = disk['name']
        if disk['type'] in ('M', 'C'):
            volumeclass = OpenvStorageISO
        elif disk['type'] == 'P':
            volumeclass = PhysicalVolume
        elif disk['type'] == 'D':
            name = str(disk['id'])


        volume = volumeclass(id=disk['referenceId'],
                             name=name, size=disk['sizeMax'],
                             driver=provider,
                             extra={'node': node},
                             iotune=disk['iotune'],
                             order=disk['order'])
        return volume

    @authenticator.auth(acl={'account': set('C')})
    def create(self, accountId, gid, name, description, size=10, type='D', ssdSize=0, iops=2000, **kwargs):
        """
        Create a disk

        :param accountId: id of account
        :param gid :id of the grid
        :param diskName: name of disk
        :param description: optional description of disk
        :param size: size in GBytes, default is 10
        :param type: (B;D;T)  B=Boot;D=Data;T=Temp, default is B
        :return the id of the created disk

        """
        # Validate that enough resources are available in the account CU limits to add the disk
        j.apps.cloudapi.accounts.checkAvailableMachineResources(accountId, vdisksize=size)
        disk, _ = self._create(accountId, gid, name, description, size, type, iops)
        return disk.id

    def _create(self, accountId, gid, name, description, size=10, type='D', iops=2000, physicalSource=None, nid=None, order=None, **kwargs):
        if size > 2000 and type != 'P':
            raise exceptions.BadRequest("Disk size can not be bigger than 2000 GB")
        if type == 'P' and not (physicalSource and nid):
            raise exceptions.BadRequest("Need to specify both node id and physical source for disk of type 'P'")

        disk = self.models.disk.new()
        disk.name = name
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        disk.gid = gid
        disk.order = order
        disk.status = 'MODELED'
        disk.iotune = {'total_iops_sec': iops}
        disk.accountId = accountId
        disk.id = self.models.disk.set(disk)[0]
        try:
            provider = self.cb.getProviderByGID(gid)
            if type == 'P':
                volumeid = 'file://{source}?id={nid}'.format(source=physicalSource, nid=nid)
                disk.referenceId = volumeid
                volume = self.getStorageVolume(disk, provider)
            else:
                volume = provider.create_volume(disk.sizeMax, disk.id)
                volume.iotune = disk.iotune
                disk.referenceId = volume.id
            disk.status = 'CREATED'
        except:
            disk.status = "DELETED"
            self.models.disk.delete(disk.id)
            raise
        self.models.disk.set(disk)
        return disk, volume

    @authenticator.auth(acl={'account': set('C')})
    def limitIO(self, diskId, iops, total_bytes_sec, read_bytes_sec, write_bytes_sec, total_iops_sec,
                read_iops_sec, write_iops_sec, total_bytes_sec_max, read_bytes_sec_max,
                write_bytes_sec_max, total_iops_sec_max, read_iops_sec_max,
                write_iops_sec_max, size_iops_sec, **kwargs):
        args = locals()

        # validate combinations
        if (iops or total_iops_sec) and (read_iops_sec or write_iops_sec):
            raise exceptions.BadRequest("total and read/write of iops_sec cannot be set at the same time")
        if (total_bytes_sec) and (read_bytes_sec or write_bytes_sec):
            raise exceptions.BadRequest("total and read/write of bytes_sec cannot be set at the same time")
        if (total_bytes_sec_max) and (read_bytes_sec_max or write_bytes_sec_max):
            raise exceptions.BadRequest("total and read/write of bytes_sec_max cannot be set at the same time")
        if (total_iops_sec_max) and (read_iops_sec_max or write_iops_sec_max):
            raise exceptions.BadRequest("total and read/write of iops_sec_max cannot be set at the same time")

        # validate iops
        for arg, val in args.items():
            if arg in ('iops', 'total_iops_sec', 'read_iops_sec', 'write_iops_sec', 'total_iops_sec_max', 'read_iops_sec_max', 'write_iops_sec_max', 'size_iops_sec'):
                if val and val < MIN_IOPS:
                    raise exceptions.BadRequest("{arg} was set below the minimum iops {min_iops}: {provided_iops} provided".format(
                        arg=arg, min_iops=MIN_IOPS, provided_iops=val))

        iotune = args
        iotune.pop('diskId')
        iotune.pop('kwargs')
        iotune.pop('self')
        iops = iotune.pop('iops')
        if iops:
            iotune['total_iops_sec'] = iops
        disk = self.models.disk.get(diskId)
        if disk.status == 'DELETED':
            raise exceptions.BadRequest("Disk with id %s is not created" % diskId)

        if disk.type == 'M':
            raise exceptions.BadRequest("Can't limitIO on a disk of type Meta")

        machine = next(iter(self.models.vmachine.search({'disks': diskId})[1:]), None)
        if not machine:
            raise exceptions.NotFound("Could not find virtual machine beloning to disk")

        disk.iotune = iotune
        self.models.disk.set(disk)
        provider, node, machine = self.cb.getProviderAndNode(machine['id'])
        volume = self.getStorageVolume(disk, provider, node)
        return provider.ex_limitio(volume)

    @authenticator.auth(acl={'account': set('R')})
    def get(self, diskId, **kwargs):
        """
        Get disk details

        :param diskId: id of the disk
        :return: dict with the disk details
        """
        if not self.models.disk.exists(diskId):
            raise exceptions.NotFound('Can not find disk with id %s' % diskId)
        return self.models.disk.get(diskId).dump()

    @authenticator.auth(acl={'account': set('R')})
    def list(self, accountId, type, **kwargs):
        """
        List the created disks belonging to an account

        :param accountId: id of accountId the disks belongs to
        :param type: type of type of the disks
        :return: list with every element containing details of a disk as a dict
        """
        query = {'accountId': {'$in': [accountId, None]}, 'status': {'$ne': 'DELETED'}}
        if type:
            query['type'] = type
        disks = self.models.disk.search(query)[1:]
        diskids = [disk['id'] for disk in disks]
        query = {'disks': {'$in': diskids}}
        vms = self.models.vmachine.search({'$query': query, '$fields': ['disks', 'id']})[1:]
        vmbydiskid = dict()
        for vm in vms:
            for diskid in vm['disks']:
                vmbydiskid[diskid] = vm['id']
        for disk in disks:
            disk['machineId'] = vmbydiskid.get(disk['id'])
        return disks

    @authenticator.auth(acl={'cloudspace': set('X')})
    def delete(self, diskId, detach, **kwargs):
        """
        Delete a disk

        :param diskId: id of disk to delete
        :param detach: detach disk from machine first
        :return True if disk was deleted successfully
        """
        if not self.models.disk.exists(diskId):
            return True
        disk = self.models.disk.get(diskId)
        if disk.status == 'DELETED':
            return True
        machines = self.models.vmachine.search({'disks': diskId, 'status': {'$ne': 'DESTROYED'}})[1:]
        if machines and not detach:
            raise exceptions.Conflict('Can not delete disk which is attached')
        elif machines:
            j.apps.cloudapi.machines.detachDisk(machineId=machines[0]['id'], diskId=diskId, **kwargs)
            disk.status = 'CREATED'
        provider = self.cb.getProviderByGID(disk.gid)
        volume = self.getStorageVolume(disk, provider)
        disk.status = 'TOBEDELETED'
        self.models.disk.set(disk)
        provider.destroy_volume(volume)
        disk.status = 'DELETED'
        self.models.disk.set(disk)
        return True

    @authenticator.auth(acl={'account': set('C')})
    def resize(self, diskId, size, **kwargs):
        """
        Resize a Disk
        stop and start required for the changes to be reflected
        :param diskId: id of disk to delete
        :param size: the new size of the disk in GB
        """
        if size > 2000:
            raise exceptions.BadRequest('Size can not be more than 2TB')
        disk = self.models.disk.get(diskId)
        if disk.type == 'M':
            raise exceptions.BadRequest("Can't resize a disk of type Meta")
        if disk.sizeMax >= size:
            raise exceptions.BadRequest("The specified size is smaller than or equal the original size")
        if disk.status == 'DELETED':
            raise exceptions.BadRequest("Disk with id %s is not created" % diskId)

        machine = next(iter(self.models.vmachine.search({'disks': diskId})[1:]), None)
        if machine:
            # Validate that enough resources are available in the CU limits to add the disk
            j.apps.cloudapi.cloudspaces.checkAvailableMachineResources(machine['cloudspaceId'], vdisksize=size)
            provider, _, _ = self.cb.getProviderAndNode(machine['id'])
            machine_id = machine['referenceId']
        else:
            # Validate that enough resources are available in the CU limits to add the disk
            j.apps.cloudapi.accounts.checkAvailableMachineResources(disk.accountId, vdisksize=size)
            provider = self.cb.getProviderByGID(disk.gid)
            machine_id = None

        volume = self.getStorageVolume(disk, provider)
        disk.sizeMax = size
        disk_info = {'referenceId': disk.referenceId, 'machineRefId': machine_id}
        res = provider.ex_extend_disk(volume.vdiskguid, size, disk_info)
        self.models.disk.set(disk)
        if not res:
            raise exceptions.Accepted(False)
        return True
