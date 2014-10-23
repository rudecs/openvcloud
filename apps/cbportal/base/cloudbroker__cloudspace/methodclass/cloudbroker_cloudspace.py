from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib import network
import urlparse
import urllib

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

        #delete network information
        networkguid = '%s_%s' % (cloudspace['gid'], cloudspace['networkId'])
        if self.vfwcl.virtualfirewall.exists(networkguid):
            vfw = self.vfwcl.virtualfirewall.get(networkguid)
            vfw.state = 'DESTROYED'
            self.vfwcl.virtualfirewall.set(vfw)


        cloudspace['networkId'] = None
        cloudspace['publicipaddress'] = None
        self.cbcl.cloudspace.set(cloudspace)
        return True


    def moveVirtualFirewallToFirewallNode(self, cloudspaceId, targetNode, **kwargs):
        """
        move the virtual firewall of a cloudspace to a different firewall node
        param:cloudspaceId id of the cloudspace
        param:targetNode name of the firewallnode the virtual firewall has to be moved to
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method moveVirtualFirewallToFirewallNode")
    
    def addExtraIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Adds an available public IP address
        param:cloudspaceId id of the cloudspace
        param:ipaddress only needed if a specific IP address needs to be assigned to this space
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addExtraIP")

    def removeIP(self, cloudspaceId, ipaddress, **kwargs):
        """
        Removed a public IP address from the cloudspace
        param:cloudspaceId id of the cloudspace
        param:ipaddress public IP address to remove from this cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method removeIP")
    
    def restoreVirtualFirewall(self, cloudspaceId, **kwargs):
        """
        Restore the virtual firewall of a cloudspace on an available firewall node
        param:cloudspaceId id of the cloudspace
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method restoreVirtualFirewall")

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
        user = self.syscl.user.simpleSearch({'name':access})
        if not user:
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Username "%s" not found' % access
        self.cloudspaces_actor.create(accountId, location, name, access, maxMemoryCapacity, maxDiskCapacity)
        return True
    
