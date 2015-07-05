from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor
from libcloud.compute.base import NodeAuthPassword, StorageVolume
from billingenginelib import pricing
from billingenginelib import account as accountbilling


class cloudapi_disks(BaseActor):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """
    def __init__(self):
        super(cloudapi_disks, self).__init__()
        self.osisclient = j.core.portal.active.osis
        self.acl = j.clients.agentcontroller.get()
        self.osis_logs = j.clients.osis.getCategory(self.osisclient, "system", "log")
        self._pricing = pricing.pricing()
        self._accountbilling = accountbilling.account()
        self._minimum_days_of_credit_required = float(self.hrd.get("instance.openvcloud.cloudbroker.creditcheck.daysofcreditrequired"))
        self.netmgr = j.apps.jumpscale.netmgr

    def getStorageVolume(self, disk, provider, node=None):
        return StorageVolume(id=disk.referenceId, name=disk.name, size=disk.sizeMax, driver=provider.client, extra={'node': node})

    @authenticator.auth(acl='C')
    @audit()
    def create(self, accountId, gid, name, description, size=10, type='D', **kwargs):
        """
        Create a disk
        param:accountId id of account
        param:gid id of the grid
        param:diskName name of disk
        param:description optional description
        param:size size in GByte default=10
        param:type (B;D;T)  B=Boot;D=Data;T=Temp default=B
        result int

        """
        disk, volume = self._create(accountId, gid, name, description, size, type)
        return disk.id

    def _create(self, accountId, gid, name, description, size=10, type='D', **kwargs):
        disk = self.models.disk.new()
        disk.name = name
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        disk.gid = gid
        disk.accountId = accountId
        diskid = self.models.disk.set(disk)[0]
        disk = self.models.disk.get(diskid)
        try:
            provider, node = self.cb.getProviderByGID(gid)
            volume = provider.client.create_volume(disk.sizeMax, disk.id)
            disk.referenceId = volume.id
        except:
            self.models.disk.delete(disk.id)
            raise
        self.models.disk.set(disk)
        return disk, volume

    @authenticator.auth(acl='R')
    @audit()
    def get(self, diskId, **kwargs):
        ctx = kwargs['ctx']
        if not self.models.disk.exists(diskId):
            ctx.start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return 'Can not find disk with id %s' % diskId
        return self.models.disk.get(diskId).dump()

    @authenticator.auth(acl='R')
    @audit()
    def list(self, accountId, type, **kwargs):
        query = {'accountId': accountId}
        if type:
            query['type'] = type
        return self.models.disk.search(query)[1:]

    @authenticator.auth(acl='D')
    @audit()
    def delete(self, diskId, dettach, **kwargs):
        """
        Delete a disk from machine
        param:machineId id of machine
        param:diskId id of disk to delete
        result bool

        """
        ctx = kwargs['ctx']
        if not self.models.disk.exists(diskId):
            return True
        disk = self.models.disk.get(diskId)
        machines = self.models.vmachine.search({'disks': diskId})[1:]
        if machines and not dettach:
            ctx.start_response('409 Conflict', [('Content-Type', 'text/plain')])
            return 'Can not delete disk which is attached'
        elif machines:
            res = j.apps.cloudapi.machines.detachDisk(machineId=machines[0]['id'], diskId=diskId, **kwargs)
            if ctx.response_started:
                return res
        provider = self.cb.getProviderByGID(disk.gid)
        volume = self.getStorageVolume(disk, provider)
        provider.client.destroy_volume(volume)
        self.models.disk.delete(diskId)
        return True
