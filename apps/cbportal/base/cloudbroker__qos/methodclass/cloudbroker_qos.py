from JumpScale import j
from JumpScale.portal.portal import exceptions
import itertools


class cloudbroker_qos(object):
    def __init__(self):
        self.acl = j.clients.agentcontroller.get()
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        self.vcl = j.clients.osis.getNamespace('vfw')

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
        disk = self.ccl.disk.get(diskId)
        if disk.status != 'CREATED':
            raise exceptions.ValueError("Disk with id %s is not created" % diskId)

        machine = next(iter(self.ccl.vmachine.search({'disks': diskId})[1:]), None)
        if not machine:
            raise ValueError("Could not find virtual machine beloning to disk")
        stack = self.ccl.stack.get(machine['stackId'])
        job = self.acl.executeJumpscript('cloudscalers', 'limitdiskio', role='storagedriver',
                                         gid=stack.gid, nid=int(stack.referenceId),
                                         args={'disks': [disk.referenceId], 'machineid': machine['referenceId']})
        return job['result']

    def limitInternalBandwith(self, cloudspaceId, machineId, rate, burst, **kwargs):
        """
        This will put a limit on the VIF of all VMs within the cloudspace
        Pass either cloudspaceId or machineId depending what you want to filter down.
        param:cloudspaceId Id of the cloudspace to limit
        param:rate maximum speed in kilobytes per second, 0 means unlimited
        param:burst maximum speed in kilobytes per second, 0 means unlimited
        result bool
        """
        if [bool(machineId), bool(cloudspaceId)].count(True) != 1:
            raise exceptions.ValueError("Either cloudspaceId or machineId should be given")

        machines = []
        query = {'status': 'RUNNING'}
        if machineId:
            query['id'] = machineId
        else:
            query['cloudspaceId'] = cloudspaceId
        machines = self.ccl.vmachine.search(query)[1:]
        stackids = list(set(vm['stackId'] for vm in machines))
        stacks = {stack['id']: stack for stack in self.ccl.stack.search({'id': {'$in': stackids}})[1:]}

        for stackId, machines in itertools.groupby(machines, lambda vm: vm['stackId']):
            stack = stacks.get(stackId)
            if stack:
                machineids = [vm['referenceId'] for vm in machines]
                args = {'machineids': machineids, 'rate': rate, 'burst': burst}
                self.acl.execute('cloudscalers', 'limitnics',
                                 gid=stack['gid'], nid=int(stack['referenceId']),
                                 args=args)
        return True

    def limitInternetBandwith(self, cloudspaceId, rate, burst, **kwargs):
        """
        This will put a limit on the outgoing traffic on the public VIF of the VFW on the physical machine
        param:cloudspaceId Id of the cloudspace to limit
        param:reate maximum speeds in kilobytes per second, 0 means unlimited
        param:burst maximum speed in kilobytes per second, 0 means unlimited
        result bool
        """
        cloudspace = self.ccl.cloudspace.get(cloudspaceId)
        vfwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        if not self.vcl.virtualfirewall.exists(vfwid):
            raise exceptions.NotFound("VFW for cloudspace %s does not exists" % cloudspaceId)
        vfw = self.vcl.virtualfirewall.get(vfwid)
        self.acl.executeJumpscript('cloudscalers', 'limitpublicnet', gid=vfw.gid, nid=vfw.nid,
                                   args={'networkId': cloudspace.networkId, 'rate': rate, 'burst': burst})
