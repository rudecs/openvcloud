from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor
from cloudbrokerlib import network

class cloudbroker_cloudspace(BaseActor):
    def __init__(self):
        super(cloudbroker_cloudspace, self).__init__()
        self.syscl = j.core.osis.getClientForNamespace('system')
        self.network = network.Network(self.models)
        self.vfwcl = j.core.osis.getClientForNamespace('vfw')
        self.netmgr = self.cb.actors.jumpscale.netmgr
        self.libvirt_actor = self.cb.actors.libcloud.libvirt
        self.cloudspaces_actor = self.cb.actors.cloudapi.cloudspaces

    @auth(['level1', 'level2', 'level3'])
    def destroy(self, accountname, cloudspaceName, cloudspaceId, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        cloudspaceId = int(cloudspaceId)
        accounts = self.models.account.simpleSearch({'name':accountname})
        if not accounts:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'

        accountid = accounts[0]['id']

        cloudspaces = self.models.cloudspace.simpleSearch({'name': cloudspaceName, 'id': cloudspaceId, 'accountId': accountid})
        if not cloudspaces:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with name %s and id %s that has account %s not found' % (cloudspaceName, cloudspaceId, accountname)

        cloudspace = cloudspaces[0]

        cloudspace['status'] = 'DESTROYED'
        self.models.cloudspace.set(cloudspace)

        #delete routeros
        gid = cloudspace['gid']
        self._destroyVFW(gid, cloudspaceId)
        if cloudspace['networkId']:
            self.libvirt_actor.releaseNetworkId(gid, cloudspace['networkId'])
        if cloudspace['publicipaddress']:
            self.network.releasePublicIpAddress(cloudspace['publicipaddress'])

        #delete machines
        for machine in self.models.vmachine.simpleSearch({'cloudspaceId':cloudspaceId}):
            machineId = machine['id']
            j.apps.cloudbroker.machine.destroy(accountname, cloudspaceName, machineId, reason)

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
    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNid, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNode name of the firewallnode the virtual firewall has to be moved to
        """
        ctx = kwargs["ctx"]
        headers = [('Content-Type', 'application/json'), ]
        cloudspace = self.models.cloudspace.get(int(cloudspaceId))
        if cloudspace.status != 'DEPLOYED':
            ctx.start_response("400", headers)
            return 'Could not move fw for cloudspace which is not deployed'

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
    def deployVFW(self, cloudspaceId, **kwargs):
        """
        Deploy VFW 
        param:cloudspaceId id of the cloudspace
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with id %s not found' % (cloudspaceId)

        return self.cloudspaces_actor.deploy(cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    def resetVFW(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with id %s not found' % (cloudspaceId)

        self.destroyVFW(cloudspaceId, **kwargs)
        return self.cloudspaces_actor.deploy(cloudspaceId)

    @auth(['level1', 'level2', 'level3'])
    def destroyVFW(self, cloudspaceId, **kwargs):
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with id %s not found' % (cloudspaceId)

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
    def create(self, accountname, location, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Create a cloudspace
        param:accountname name of account to create space for
        param:name name of space to create
        param:access username which has full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        """
        ctx = kwargs["ctx"]
        account = self.models.account.simpleSearch({'name':accountname})
        if not account:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'
        accountId = account[0]['id']
        user = self.syscl.user.simpleSearch({'id':access})
        if not user:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Username "%s" not found' % access
        self.cloudspaces_actor.create(accountId, location, name, access, maxMemoryCapacity, maxDiskCapacity)
        return True

    def _checkUser(self, username):
        user = self.syscl.user.simpleSearch({'id':username})
        if not user:
            return False, 'Username "%s" not found' % username
        return True, user[0]
    
    @auth(['level1', 'level2', 'level3'])
    def addUser(self, cloudspaceId, username, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountname id of the account
        param:username id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        ctx = kwargs["ctx"]
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return "Cloud space with id %s doest not exists" % cloudspaceId

        check, result = self._checkUser(username)
        if not check:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return result
        userId = result['id']
        self.cloudspaces_actor.addUser(cloudspaceId, userId, accesstype)
        return True

    @auth(['level1', 'level2', 'level3'])
    def deleteUser(self, cloudspaceId, username, **kwargs):
        """
        Delete a user from the account
        """
        ctx = kwargs["ctx"]
        cloudspaceId = int(cloudspaceId)
        if not self.models.cloudspace.exists(cloudspaceId):
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return "Cloud space with id %s doest not exists" % cloudspaceId
        check, result = self._checkUser(username)
        if not check:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return result
        userId = result['id']
        self.cloudspaces_actor.deleteUser(cloudspaceId, userId)
        return True
