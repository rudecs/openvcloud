from JumpScale import j
from cloudbrokerlib import authenticator
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal.async import async
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
from cloudbrokerlib import network
from JumpScale.portal.portal import exceptions


class cloudbroker_cloudspace(BaseActor):

    def __init__(self):
        super(cloudbroker_cloudspace, self).__init__()
        self.syscl = j.clients.osis.getNamespace('system')
        self.network = network.Network(self.models)
        self.vfwcl = j.clients.osis.getNamespace('vfw')
        self.netmgr = self.cb.actors.jumpscale.netmgr
        self.libvirt_actor = self.cb.actors.libcloud.libvirt
        self.cloudspaces_actor = self.cb.actors.cloudapi.cloudspaces
        self.actors = self.cb.actors.cloudapi

    def _getCloudSpace(self, cloudspaceId):
        cloudspaceId = int(cloudspaceId)

        cloudspaces = self.models.cloudspace.simpleSearch({'id': cloudspaceId})
        if not cloudspaces:
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = cloudspaces[0]
        return cloudspace

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def destroy(self, accountId, cloudspaceId, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        cloudspace = self._getCloudSpace(cloudspaceId)

        ctx = kwargs['ctx']
        ctx.events.runAsync(self._destroy,
                            args=(cloudspace, reason, ctx),
                            kwargs={},
                            title='Deleting Cloud Space',
                            success='Finished deleting Cloud Space',
                            error='Failed to delete Cloud Space')

    def _destroy(self, cloudspace, reason, ctx):
        with self.models.cloudspace.lock(cloudspace['id']):
            cloudspace = self.models.cloudspace.get(cloudspace['id']).dump()
            if cloudspace['status'] == 'DEPLOYING':
                raise exceptions.BadRequest('Can not delete a CloudSpace that is being deployed.')
        status = cloudspace['status']
        cloudspace['status'] = 'DESTROYING'
        self.models.cloudspace.set(cloudspace)
        title = 'Deleting Cloud Space %(name)s' % cloudspace
        try:
            # delete machines
            machines = self.models.vmachine.search(
                {'cloudspaceId': cloudspace['id'], 'status': {'$ne': 'DESTROYED'}})[1:]
            for idx, machine in enumerate(sorted(machines, key=lambda m: m['cloneReference'], reverse=True)):
                machineId = machine['id']
                if machine['status'] != 'DESTROYED':
                    ctx.events.sendMessage(title, 'Deleting Virtual Machine %s/%s' % (idx + 1, len(machines)))
                    j.apps.cloudbroker.machine.destroy(machineId, reason)
        except:
            cloudspace = self.models.cloudspace.get(cloudspace['id']).dump()
            cloudspace['status'] = status
            self.models.cloudspace.set(cloudspace)
            raise

        # delete routeros
        ctx.events.sendMessage(title, 'Deleting Virtual Firewall')
        self._destroyVFW(cloudspace['gid'], cloudspace['id'])
        cloudspace = self.models.cloudspace.get(cloudspace['id'])
        cloudspace.status = 'DESTROYED'
        self.cb.cloudspace.release_resources(cloudspace)
        self.models.cloudspace.set(cloudspace)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def destroyCloudSpaces(self, cloudspaceIds, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        ctx = kwargs['ctx']
        ctx.events.runAsync(self._destroyCloudSpaces,
                            args=(cloudspaceIds, reason, ctx),
                            kwargs={},
                            title='Destroying Cloud Spaces',
                            success='Finished destroying Cloud Spaces',
                            error='Failed to destroy Cloud Space')

    def _destroyCloudSpaces(self, cloudspaceIds, reason, ctx):
        for idx, cloudspaceId in enumerate(cloudspaceIds):
            cloudspace = self._getCloudSpace(cloudspaceId)
            self._destroy(cloudspace, reason, ctx)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    @async('Moving Virtual Firewall', 'Finished moving VFW', 'Failed to move VFW')
    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNid, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNode name of the firewallnode the virtual firewall has to be moved to
        """
        cloudspace = self.models.cloudspace.get(int(cloudspaceId))
        if cloudspace.status != 'DEPLOYED':
            raise exceptions.BadRequest('Could not move fw for cloudspace which is not deployed')

        fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
        self.netmgr.fw_move(fwid, int(targetNid))
        return True

    @auth(['level1', 'level2', 'level3'])
    def addExtraIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Adds an available public IP address
        param:cloudspaceId id of the cloudspace
        param:ipaddress only needed if a specific IP address needs to be assigned to this space
        """
        return True

    @auth(['level1', 'level2', 'level3'])
    def removeIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Removed a public IP address from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:ipaddress public IP address to remove from this cloudspace
        """
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    @async('Deploying Cloud Space', 'Finished deploying Cloud Space', 'Failed to deploy Cloud Space')
    def deployVFW(self, cloudspaceId, **kwargs):
        """
        Deploy VFW
        param:cloudspaceId id of the cloudspace
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        return self.cloudspaces_actor.deploy(cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    @async('Redeploying Cloud Space', 'Finished redeploying Cloud Space', 'Failed to redeploy Cloud Space')
    def resetVFW(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        self.destroyVFW(cloudspaceId, **kwargs)
        self.cloudspaces_actor.deploy(cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def startVFW(self, cloudspaceId, **kwargs):
        """
        Start VFW
        param:cloudspaceId id of the cloudspace
        """
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        return j.apps.jumpscale.netmgr.fw_start(fwid)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def stopVFW(self, cloudspaceId, **kwargs):
        """
        Stop VFW
        param:cloudspaceId id of the cloudspace
        """
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = '%s_%s' % (cloudspace.gid, cloudspace.networkId)
        return j.apps.jumpscale.netmgr.fw_stop(fwid)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def destroyVFW(self, cloudspaceId, **kwargs):
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        self._destroyVFW(cloudspace.gid, cloudspaceId)
        self.cb.cloudspace.release_resources(cloudspace, False)
        cloudspace.status = 'VIRTUAL'
        self.models.cloudspace.set(cloudspace)
        return True

    def _destroyVFW(self, gid, cloudspaceId):
        fws = self.netmgr.fw_list(int(gid), str(cloudspaceId))
        if fws:
            self.netmgr.fw_delete(fws[0]['guid'], gid)
            return True
        return False

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def update(self, cloudspaceId, name, maxMemoryCapacity, maxVDiskCapacity, maxCPUCapacity,
               maxNetworkPeerTransfer, maxNumPublicIP, allowedVMSizes, **kwargs):
        """
        Update a cloudspace name or the maximum cloud units set on it
        Setting a cloud unit maximum to -1 will not put any restrictions on the resource

        :param cloudspaceId: id of the cloudspace to change
        :param name: name of the cloudspace
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return: True if update was successful
        """

        resourcelimits = {'CU_M': maxMemoryCapacity,
                          'CU_D': maxVDiskCapacity,
                          'CU_C': maxCPUCapacity,
                          'CU_NP': maxNetworkPeerTransfer,
                          'CU_I': maxNumPublicIP}
        self.cb.fillResourceLimits(resourcelimits, preserve_none=True)
        maxMemoryCapacity = resourcelimits['CU_M']
        maxVDiskCapacity = resourcelimits['CU_D']
        maxCPUCapacity = resourcelimits['CU_C']
        maxNetworkPeerTransfer = resourcelimits['CU_NP']
        maxNumPublicIP = resourcelimits['CU_I']

        return self.cloudspaces_actor.update(cloudspaceId, name, maxMemoryCapacity,
                                             maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer, maxNumPublicIP, allowedVMSizes)

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def create(self, accountId, location, name, access, maxMemoryCapacity=-1, maxVDiskCapacity=-1,
               maxCPUCapacity=-1, maxNetworkPeerTransfer=-1, maxNumPublicIP=-1, externalnetworkId=None, allowedVMSizes=[], **kwargs):
        """
        Create a cloudspace

        :param accountId: id of account to create space for
        :param name: name of space to create
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :param allowedVMSizes: alowed sizes for a cloudspace
        :return: True if update was successful
        """
        user = self.syscl.user.search({'id': access})[1:]
        if not user:
            raise exceptions.NotFound('Username "%s" not found' % access)

        resourcelimits = {'CU_M': maxMemoryCapacity,
                          'CU_D': maxVDiskCapacity,
                          'CU_C': maxCPUCapacity,
                          'CU_NP': maxNetworkPeerTransfer,
                          'CU_I': maxNumPublicIP}
        self.cb.fillResourceLimits(resourcelimits)
        maxMemoryCapacity = resourcelimits['CU_M']
        maxVDiskCapacity = resourcelimits['CU_D']
        maxCPUCapacity = resourcelimits['CU_C']
        maxNetworkPeerTransfer = resourcelimits['CU_NP']
        maxNumPublicIP = resourcelimits['CU_I']

        return self.cloudspaces_actor.create(accountId, location, name, access, maxMemoryCapacity,
                                             maxVDiskCapacity, maxCPUCapacity, maxNetworkPeerTransfer,
                                             maxNumPublicIP, externalnetworkId, allowedVMSizes)

    def _checkCloudspace(self, cloudspaceId):
        cloudspaces = self.models.cloudspace.search({'id': cloudspaceId})[1:]
        if not cloudspaces:
            raise exceptions.NotFound("Cloud space with id %s does not exists" % cloudspaceId)

        return cloudspaces[0]

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def addUser(self, cloudspaceId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountname id of the account
        param:username id of the user to give access or emailaddress to invite an external user
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        cloudspace = self._checkCloudspace(cloudspaceId)
        cloudspaceId = cloudspace['id']
        user = self.cb.checkUser(username, activeonly=False)

        cloudspaceacl = authenticator.auth().getCloudspaceAcl(cloudspaceId)
        if username in cloudspaceacl:
            updated = self.cloudspaces_actor.updateUser(cloudspaceId, username, accesstype)
            if not updated:
                raise exceptions.PreconditionFailed('User already has same access level to owning '
                                                    'account')
        elif user:
            self.cloudspaces_actor.addUser(cloudspaceId, username, accesstype)
        elif self.cb.isValidEmailAddress(username):
            self.cloudspaces_actor.addExternalUser(cloudspaceId, username, accesstype)
        else:
            raise exceptions.NotFound('User with username %s is not found' % username)

        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def deleteUser(self, cloudspaceId, username, recursivedelete, **kwargs):
        """
        Delete a user from the account
        """
        cloudspace = self._checkCloudspace(cloudspaceId)
        cloudspaceId = cloudspace['id']
        user = self.cb.checkUser(username)
        if user:
            userId = user['id']
        else:
            # external user, delete ACE that was added using emailaddress
            userId = username
        self.cloudspaces_actor.deleteUser(cloudspaceId, userId, recursivedelete)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def deletePortForward(self, cloudspaceId, publicIp, publicPort, proto, **kwargs):
        return self.actors.portforwarding.deleteByPort(cloudspaceId, publicIp, publicPort, proto)
