from JumpScale import j
import netaddr
json = j.db.serializers.ujson
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor

class cloudbroker_iaas(BaseActor):
    """
    gateway to grid
    """
    def addPublicNetwork(self, gid, network, gateway, startip, endip, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        """
        try:
            net = netaddr.IPNetwork(network)
        except:
            raise exceptions.BadRequest("Invalid network given %s" % network)

        def checkIP(ip, name):
            try:
                if ip not in net:
                    raise exceptions.BadRequest("%s not in network" % name)
            except netaddr.AddrFormatError:
                raise exceptions.BadRequest("Invalid %s given" % name)

        checkIP(startip, 'Start IP Address')
        checkIP(endip, 'End IP Address')
        checkIP(gateway, 'Gateway')

        pool = self.models.publicipv4pool.new()
        pool.id = str(net.cidr)
        pool.gid = gid
        pool.gateway = gateway
        pool.subnetmask = str(net.netmask)
        pool.network = str(net.network)
        pool.pubips = [str(ip) for ip in netaddr.IPRange(startip, endip)]
        self.models.publicipv4pool.set(pool)
        return True

    def addPublicIPv4IPS(self, subnet, freeips, **kwargs):
        """
        Add public ips to an existing range
        """
        ctx = kwargs["ctx"]
        if not self.models.publicipv4pool.exists(subnet):
            ctx.start_response("404 Not Found")
            return "Could not find PublicIPv4Pool with subnet %s" % subnet
        net = netaddr.IPNetwork(subnet)
        if not checkIPS(net, freeips):
            ctx.start_response("400 Bad Request")
            return "One or more IP Addresses %s is not in subnet %s" % (subnet)
        pool = self.models.publicipv4pool.get(subnet)
        pool.pubips = list(set(pool.pubips).union(set(freeips)))
        self.models.publicipv4pool.set(pool)
        return subnet

    def removePublicIPv4IPS(self, subnet, freeips, **kwargs):
        """
        Remove public ips from an existing range
        """
        ctx = kwargs["ctx"]
        if not self.models.publicipv4pool.exists(subnet):
            ctx.start_response("404 Not Found")
            return "Could not find PublicIPv4Pool with subnet %s" % subnet
        net = netaddr.IPNetwork(subnet)
        if not checkIPS(net, freeips):
            ctx.start_response("400 Bad Request")
            return "One or more IP Addresses %s is not in subnet %s" % (subnet)
        pool = self.models.publicipv4pool.get(subnet)
        pool.pubips = list(set(pool.pubips) - set(freeips))
        self.models.publicipv4pool.set(pool)
        return subnet

    @auth(['level1', 'level2', 'level3'])
    def syncAvailableImagesToCloudbroker(self, **kwargs):
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        result boolean
        """
        stacks = self.models.stack.list()
        for stack in stacks:
            self.cb.stackImportImages(stack)
        return True
    
    @auth(['level1', 'level2', 'level3'])
    def syncAvailableSizesToCloudbroker(self, **kwargs):
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        result boolean
        """
        stacks = self.models.stack.list()
        for stack in stacks:
            self.cb.stackImportSizes(stack)
        return True