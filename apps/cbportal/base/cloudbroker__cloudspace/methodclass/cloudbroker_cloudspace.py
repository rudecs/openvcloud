from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib import network

class cloudbroker_cloudspace(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="cloudspace"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.syscl = j.core.osis.getClientForNamespace('system')
        self.network = network.Network(self.cbcl)
        self.vfwcl = j.core.osis.getClientForNamespace('vfw')
        self._cb = None
        self.netmgr = self.cb.extensions.imp.actors.jumpscale.netmgr
        self.libvirt_actor = self.cb.extensions.imp.actors.libcloud.libvirt
        self.cloudspaces_actor = self.cb.extensions.imp.actors.cloudapi.cloudspaces

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1', 'level2'])
    def destroy(self, accountname, cloudspaceName, cloudspaceId, reason, **kwargs):
        """
        Destroys a cloudspacec and its machines, vfws and routeros
        """
        cloudspaceId = int(cloudspaceId)
        accounts = self.cbcl.account.simpleSearch({'name':accountname})
        if not accounts:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'

        accountid = accounts[0]['id']

        cloudspaces = self.cbcl.cloudspace.simpleSearch({'name': cloudspaceName, 'id': cloudspaceId, 'accountId': accountid})
        if not cloudspaces:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with name %s and id %s that has account %s not found' % (cloudspaceName, cloudspaceId, accountname)

        cloudspace = cloudspaces[0]

        cloudspace['status'] = 'DESTROYED'
        self.cbcl.cloudspace.set(cloudspace)

        #delete routeros
        gid = cloudspace['gid']
        fws = self.netmgr.fw_list(gid, str(cloudspaceId))
        if fws:
            self.netmgr.fw_delete(fws[0]['guid'], gid)
        if cloudspace['networkId']:
            self.libvirt_actor.releaseNetworkId(gid, cloudspace['networkId'])
        if cloudspace['publicipaddress']:
            self.network.releasePublicIpAddress(cloudspace['publicipaddress'])

        #delete machines
        for machine in self.cbcl.vmachine.simpleSearch({'cloudspaceId':cloudspaceId}):
            machineId = machine['id']
            j.apps.cloudbroker.machine.destroy(accountname, cloudspaceName, machineId, reason)

        cloudspace['networkId'] = None
        cloudspace['publicipaddress'] = None
        self.cbcl.cloudspace.set(cloudspace)
        return True


    @auth(['level1','level2'])
    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNode, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNode name of the firewallnode the virtual firewall has to be moved to
        """
        return True
    
    @auth(['level1','level2'])
    def addExtraIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Adds an available public IP address
        param:cloudspaceId id of the cloudspace
        param:ipaddress only needed if a specific IP address needs to be assigned to this space
        """
        return True

    @auth(['level1','level2'])
    def removeIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Removed a public IP address from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:ipaddress public IP address to remove from this cloudspace
        """
        return True
    
    @auth(['level1','level2'])
    def restoreVirtualFirewall(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        return True

    @auth(['level1','level2'])
    def destroyVFW(self, cloudpaceId, **kwargs):
        return True

    @auth(['level1','level2'])
    def updateName(self, cloudspaceId, newname, **kwargs):
        cloudspace = self.cbcl.cloudspace.get(int(cloudspaceId))
        cloudspace.name = newname
        self.cbcl.cloudspace.set(cloudspace)
        return True

    @auth(['level1','level2'])
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
        account = self.cbcl.account.simpleSearch({'name':accountname})
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
    
    @auth(['level1','level2'])
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
        if not self.cbcl.cloudspace.exists(cloudspaceId):
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

    @auth(['level1','level2'])
    def deleteUser(self, cloudspaceId, username, **kwargs):
        """
        Delete a user from the account
        """
        ctx = kwargs["ctx"]
        cloudspaceId = int(cloudspaceId)
        if not self.cbcl.cloudspace.exists(cloudspaceId):
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
