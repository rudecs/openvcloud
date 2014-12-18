from JumpScale import j
import netaddr
json = j.db.serializers.ujson
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor

def checkIPS(network, ips):
    for ip in ips:
        if netaddr.IPAddress(ip) not in network:
            return False
    return True

class cloudbroker_iaas(BaseActor):
    """
    gateway to grid
    """
    def addPublicIPv4Subnet(self, subnet, gateway, freeips, gid, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        """
        ctx = kwargs["ctx"]
        net = netaddr.IPNetwork(subnet)
        if isinstance(freeips, basestring):
            freeips = [ip.strip() for ip in freeips.split(',')]
        if not checkIPS(net, freeips):
            ctx.start_response("400 Bad Request")
            return "One or more IP Addresses %s is not in subnet %s" % (subnet)
        if not checkIPS(net, [gateway]):
            ctx.start_response("400 Bad Request")
            return "Gateway Address %s is not in subnet %s" % (gateway, subnet)

        pool = self.models.publicipv4pool.new()
        pool.id = subnet
        pool.gid = int(gid)
        pool.gateway = gateway
        pool.subnetmask = str(net.netmask)
        pool.network = str(net.network)
        pool.pubips = list(set(freeips))
        self.models.publicipv4pool.set(pool)
        return subnet

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
