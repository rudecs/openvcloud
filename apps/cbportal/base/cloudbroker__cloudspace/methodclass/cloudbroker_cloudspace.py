from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
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

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def destroy(self, accountId, cloudspaceId, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """

        cloudspaceId = int(cloudspaceId)

        accountid = accountId

        cloudspaces = self.models.cloudspace.simpleSearch({ 'id': cloudspaceId, 'accountId': accountid})
        if not cloudspaces:
            raise exceptions.NotFound('Cloudspace with id %s that has accountId %s not found' % (cloudspaceId, accountId))

        cloudspace = cloudspaces[0]

        status = cloudspace['status']
        cloudspace['status'] = 'DESTROYED'
        self.models.cloudspace.set(cloudspace)

        try:
            #delete machines
            for machine in self.models.vmachine.simpleSearch({'cloudspaceId':cloudspaceId}):
                machineId = machine['id']
                if machine['status'] != 'DESTROYED':
                    j.apps.cloudbroker.machine.destroy(machineId, reason)
        except:
            cloudspace['status'] = status
            self.models.cloudspace.set(cloudspace)
            raise

        #delete routeros
        gid = cloudspace['gid']
        self._destroyVFW(gid, cloudspaceId)
        if cloudspace['networkId']:
            self.libvirt_actor.releaseNetworkId(gid, cloudspace['networkId'])
        if cloudspace['publicipaddress']:
            self.network.releasePublicIpAddress(cloudspace['publicipaddress'])

        cloudspace['networkId'] = None
        cloudspace['publicipaddress'] = None
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
    def resetVFW(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound('Cloudspace with id %s not found' % (cloudspaceId))

        self.destroyVFW(cloudspaceId, **kwargs)
        return self.cloudspaces_actor.deploy(cloudspaceId)

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
        if cloudspace.publicipaddress:
            self.network.releasePublicIpAddress(cloudspace.publicipaddress)
            cloudspace.publicipaddress = None
            cloudspace.status = 'VIRTUAL'
            self.models.cloudspace.set(cloudspace)
        return True

    @auth(['level1', 'level2', 'level3'])
    def updateName(self, cloudspaceId, newname, **kwargs):
        cloudspace = self.models.cloudspace.get(int(cloudspaceId))
        cloudspace.name = newname
        self.models.cloudspace.set(cloudspace)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def create(self, accountId, location, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Create a cloudspace
        param:accountname name of account to create space for
        param:name name of space to create
        param:access username which has full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        """
        account = self.models.account.get(accountId)
        user = self.syscl.user.search({'id': access})[1:]
        if not user:
            raise exceptions.NotFound('Username "%s" not found' % access)
        self.cloudspaces_actor.create(accountId, location, name, access, maxMemoryCapacity, maxDiskCapacity)
        return True

    def _checkUser(self, username):
        user = self.syscl.user.simpleSearch({'id':username})
        if not user:
            raise exceptions.NotFound('Username "%s" not found' % username)
        return user[0]
    
    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def addUser(self, cloudspaceId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountname id of the account
        param:username id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound("Cloud space with id %s doest not exists" % cloudspaceId)

        user = self._checkUser(username)
        userId = user['id']
        self.cloudspaces_actor.addUser(cloudspaceId, userId, accesstype)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def deleteUser(self, cloudspaceId, username, **kwargs):
        """
        Delete a user from the account
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            raise exceptions.NotFound("Cloud space with id %s doest not exists" % cloudspaceId)
        user = self._checkUser(username)
        userId = user['id']
        self.cloudspaces_actor.deleteUser(cloudspaceId, userId)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def deletePortForward(self, cloudspaceId, publicIp, publicPort, proto, **kwargs):
         return self.actors.portforwarding.deleteByPort(cloudspaceId, publicIp, publicPort, proto)


