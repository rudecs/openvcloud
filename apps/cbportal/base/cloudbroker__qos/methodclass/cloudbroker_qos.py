from JumpScale import j
from Jumpscale.portal.portal import exceptions


class cloudbroker_qos(object):
    def __init__(self):
        self.acl = j.clients.agentcontroller.get()
        self.ccl = j.clients.osis.getNamespace('cloudbroker')

    def limitCPU(self, machineId, **kwargs):
        """
        Limit CPU quota
        param:machineId Id of the machine to limit
        result bool
        """
        raise NotImplementedError("not implemented method limitCPU")

    def limitIO(self, diskId, iops, **kwargs):
        """
        Limit IO done on a certain disk
        param:diskId Id of the disk to limit
        param:iops Max IO per second, 0 mean unlimited
        result bool
        """
        disk = ccl.disk.get(diskId)
        if disk.status != 'CREATED':
            raise exceptions.ValueError("Disk with id %s is not created" % diskId)

        machine = next(iter(self.ccl.vmachine.search({'disks': diskId})[1:]), None)
        if not machine:
            raise ValueError("Could not find virtual machine beloning to disk")
        job = self.acl.executeJumpscript('cloudscalers', 'limitdiskio', gid=..., role='storagedriver',
                                         args={'disks': [disk.referenceId], 'machineid': machine.referenceId})
        return job['result']
        raise NotImplementedError("not implemented method limitIO")

    def limitInternalBandwith(self, cloudspaceId, machineId, maxSpeed, **kwargs):
        """
        This will put a limit on the VIF of all VMs within the cloudspace
        param:cloudspaceId Id of the cloudspace to limit
        param:maxSpeed maximum speeds in kilobytes per second, 0 means unlimited
        result bool
        """
        if not machineId and not cloudspaceId:
            raise exceptions.ValueError("Either cloudspaceId or machineId should be given")
        raise NotImplementedError("not implemented method limitInternalBandwith")

    def limitInternetBandwith(self, cloudspaceId, maxSpeed, **kwargs):
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        param:cloudspaceId Id of the cloudspace to limit
        param:maxSpeed maximum speeds in kilobytes per second, 0 means unlimited
        result bool
        """
        raise NotImplementedError("not implemented method limitInternetBandwith")
