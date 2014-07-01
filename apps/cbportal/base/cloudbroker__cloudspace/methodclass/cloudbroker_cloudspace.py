from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
from cloudbroker import network
import urlparse
import urllib

class cloudbroker_cloudspace(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="cloudspace"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.network = network.Network(self.cbcl)
        self.vfwcl = j.core.osis.getClientForNamespace('vfw')
        self._cb = None
        self.netmgr = self.cb.extensions.imp.actors.jumpscale.netmgr
        self.libvirt_actor = self.cb.extensions.imp.actors.libcloud.libvirt

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1', 'level2'])
    def destroy(self, accountname, cloudspaceName, cloudspaceId, reason, **kwargs):
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

        if str(cloudspace['location']) != j.application.config.get('cloudbroker.where.am.i'):
            ctx = kwargs["ctx"]
            params = {'accountname': accountname, 'cloudspaceName': cloudspaceName, 'cloudspaceId': cloudspaceId, 'reason': reason}
            hostname = j.application.config.getDict('cloudbroker.location.%s' % str(cloudspace['location']))
            url = '%s%s?%s' % (hostname, ctx.env['PATH_INFO'], urllib.urlencode(params))
            headers = [('Content-Type', 'application/json'), ('Location', url)]
            ctx.start_response("302", headers)
            return url

        cloudspace['status'] = 'DESTROYED'
        self.cbcl.cloudspace.set(cloudspace)

        #delete routeros
        gid = str(j.application.whoAmI.gid)
        fws = self.netmgr.fw_list(gid, str(cloudspaceId))
        if fws:
            self.netmgr.fw_delete(fws[0]['guid'], gid)
        if cloudspace['networkId']:
            self.libvirt_actor.releaseNetworkId(cloudspace['networkId'])
        if cloudspace['publicipaddress']:
            self.network.releasePublicIpAddress(cloudspace['publicipaddress'])

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
    
