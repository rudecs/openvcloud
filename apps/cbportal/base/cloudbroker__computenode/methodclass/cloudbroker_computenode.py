from JumpScale import j
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
import random
import urlparse

class cloudbroker_computenode(BaseActor):
    """
    Operator actions for handling interventsions on a computenode
    
    """
    def __init__(self):
        super(cloudbroker_computenode, self).__init__()
        self.scl = j.clients.osis.getNamespace('system')
        self._vcl = j.clients.osis.getCategory(j.core.portal.active.osis, 'vfw', 'virtualfirewall')
        self.acl = j.clients.agentcontroller.get()


    def _getStack(self, id, gid):
        stacks = self.models.stack.search({'id':int(id), 'gid': int(gid)})[1:]
        if not stacks:
            raise exceptions.NotFound('ComputeNode with id %s not found' % id)
        return stacks[0]

    @auth(['level1', 'level2', 'level3'])
    def setStatus(self, id, gid, status, **kwargs):
        """
        Set different stack statusses, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'OFFLINE(Machine is not available'
        param:statckid id of the stack to update
        param:status status e.g ENABLED, DISABLED, or OFFLINE
        result 
        """
        statusses = ['ENABLED', 'DECOMMISSIONED', 'MAINTENANCE']
        stack = self._getStack(id, gid)
        if status not in statusses:
            return exceptions.BadRequest('Invalid status %s should be in %s' % (status, ', '.join(statusses)))
        if status == 'ENABLED':
            if stack['status'] not in ('MAINTENANCE', 'ENABLED'):
                raise exceptions.PreconditionFailed("Can not enable ComputeNode in state %s" % (stack['status']))

        if status == 'DECOMMISSIONED':
            return self.decommission(id, gid, '')

        elif status == 'MAINTENANCE':
            return self.maintenance(id, gid)
        else:
            return self._changeStackStatus(stack, status)


    def _changeStackStatus(self, stack, status):
        stack['status'] = status
        self.models.stack.set(stack)
        if status in ['ENABLED', 'MAINTENANCE', 'DECOMMISSIONED']:
            nodes = self.scl.node.search({'id':int(stack['referenceId']), 'gid':stack['gid']})[1:]
            if len(nodes) > 0:
                node = nodes[0]
                node['active'] = True if status == 'ENABLED' else False
                self.scl.node.set(node)
        return stack['status']

    @auth(['level2', 'level3'], True)
    def enable(self, id, gid, message, **kwargs):
        stack = self._getStack(id, gid)
        status = self._changeStackStatus(stack, 'ENABLED')
        job = self.acl.scheduleCmd(gid, int(stack['referenceId']), 'cloudscalers', 'startallmachines', args={}, log=True, timeout=600, wait=True)
        kwargs['ctx'].events.waitForJob(job, 'Started all Virtual Machines on Node', 'Failed to start Virtual Machines', 'Enabling Node')
        kwargs['ctx'].events.sendMessage('Enabling Node', 'Starting all Virtual Machines on Node')
        return status

    @auth(['level2', 'level3'], True)
    @wrap_remote
    def maintenance(self, id, gid, vmaction, **kwargs):
        """
        :param id: stack Id
        :param gid: Grid id
        :param vmaction: what to do with vms stop or move
        :return: bool
        """
        if vmaction not in ('move', 'stop'):
            raise exceptions.BadRequest("VMAction should either be move or stop")
        stack = self._getStack(id, gid)
        self._changeStackStatus(stack, "MAINTENANCE")
        title = 'Putting Node in Maintenance'
        if vmaction == 'stop':
            job = self.acl.scheduleCmd(gid, int(stack['referenceId']), 'cloudscalers', 'stopallmachines', args={}, log=True, timeout=600, wait=True)
            kwargs['ctx'].events.waitForJob(job, 'Stopped all Virtual Machines on Node', 'Failed to stop Virtual Machines', title)
        elif vmaction == 'move':
            kwargs['ctx'].events.runAsync(self._move_virtual_machines,
                                          args=(stack, title, kwargs['ctx']),
                                          kwargs={},
                                          title='Putting Node in Maintenance',
                                          success='Successfully moved all Virtual Machines',
                                          error='Failed to move Virtual Machines')
        return True

    def _move_virtual_machines(self, stack, title, ctx):
        machines_actor = j.apps.cloudbroker.machine
        stackmachines = self.models.vmachine.search({'stackId': stack['id'],
                                                     'status': {'$nin': ['DESTROYED', 'ERROR']}
                                                    })[1:]
        othernodes = self.scl.node.search({'gid': stack['gid'], 'active': True, 'roles': 'fw'})[1:]
        if not othernodes:
            raise exceptions.ServiceUnavailable('There is no other Firewall node available to move the Virtual Firewall to')

        for machine in stackmachines:
            ctx.events.sendMessage(title, 'Moving Virtual Machine %s' % machine['name'])
            machines_actor.moveToDifferentComputeNode(machine['id'], reason='Disabling source', force=True)

        vfws = self._vcl.search({'gid': stack['gid'],
                                 'nid': int(stack['referenceId'])})[1:]
        for vfw in vfws:
            randomnode = random.choice(othernodes)
            ctx.events.sendMessage(title, 'Moving Virtual Firewal %s' % vfw['id'])
            j.apps.jumpscale.netmgr.fw_move(vfw['guid'], randomnode['id'])

    @auth(['level2', 'level3'], True)
    @wrap_remote
    def decommission(self, id, gid, message, **kwargs):
        stack = self._getStack(id, gid)
        stacks = self.models.stack.search({'gid': gid, 'status': 'ENABLED'})[1:]
        if not stacks:
            raise exceptions.PreconditionFailed("Decommissioning stack not possible when there are no other enabled stacks")
        self._changeStackStatus(stack, 'DECOMMISSIONED')
        otherstack = random.choice(filter(lambda x: x['id'] != id, stacks))
        args = {'storageip': urlparse.urlparse(stack['apiUrl']).hostname}
        job = self.acl.executeJumpscript('cloudscalers', 'ovs_put_node_offline',
                                         nid=int(otherstack['referenceId']), gid=otherstack['gid'],
                                         args=args)
        if job['state'] != 'OK':
            raise exceptions.Error("Failed to put storage node offline")

        ctx = kwargs['ctx']
        title = 'Decommissioning Node'
        ctx.events.runAsync(self._move_virtual_machines,
                            args=(stack, title, ctx),
                            kwargs={},
                            title=title,
                            success='Successfully moved all Virtual Machines.</br>Decommissioning finished.',
                            error='Failed to move all Virtual Machines')
        return True

    def btrfs_rebalance(self, name, gid, mountpoint, uuid, **kwargs):
        """
        Rebalances the btrfs filesystem
        var:name str,, name of the computenode
        var:gid int,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool
        """
        raise NotImplemented()
