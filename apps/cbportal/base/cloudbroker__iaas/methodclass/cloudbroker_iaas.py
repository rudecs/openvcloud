from JumpScale import j
from JumpScale.portal.portal import exceptions
import netaddr
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor
json = j.db.serializers.ujson


def checkIPS(network, ips):
    for ip in ips:
        if netaddr.IPAddress(ip) not in network:
            return False
    return True


class cloudbroker_iaas(BaseActor):
    """
    gateway to grid
    """
    def __init__(self):
        super(cloudbroker_iaas, self).__init__()
        self.lcl = j.clients.osis.getNamespace('libvirt')

    def addPublicIPv4Subnet(self, subnet, gateway, startip, endip, gid, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        """
        try:
            net = netaddr.IPNetwork(subnet)
            if netaddr.IPAddress(startip) not in net:
                raise exceptions.BadRequest("Start IP Addresses %s is not in subnet %s" % (startip, subnet))
            if netaddr.IPAddress(endip) not in net:
                raise exceptions.BadRequest("End IP Addresses %s is not in subnet %s" % (endip, subnet))
            if not checkIPS(net, [gateway]):
                raise exceptions.BadRequest("Gateway Address %s is not in subnet %s" % (gateway, subnet))
            if self.models.publicipv4pool.exists(subnet):
                raise exceptions.Conflict("Public IPv4 Pool with subnet already exists")
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)

        pool = self.models.publicipv4pool.new()
        pool.id = subnet
        pool.gid = int(gid)
        pool.gateway = gateway
        pool.subnetmask = str(net.netmask)
        pool.network = str(net.network)
        pool.pubips = [str(ip) for ip in netaddr.IPRange(startip, endip)]
        self.models.publicipv4pool.set(pool)
        return subnet

    def _getUsedIPS(self, pool):
        networkpool = netaddr.IPNetwork(pool.id)
        usedips = set()

        for space in self.models.cloudspace.search({'$query': {'gid': pool.gid, 'status': 'DEPLOYED'}, '$fields': ['id', 'name', 'publicipaddress']})[1:]:
            if netaddr.IPNetwork(space['publicipaddress']).ip in networkpool:
                usedips.add(str(netaddr.IPNetwork(space['publicipaddress']).ip))
        for vm in self.models.vmachine.search({'nics.type': 'PUBLIC', 'status': {'$nin': ['ERROR', 'DESTROYED']}})[1:]:
            for nic in vm['nics']:
                if nic['type'] == 'PUBLIC' and netaddr.IPNetwork(nic['ipAddress']).ip in networkpool:
                    usedips.add(str(netaddr.IPNetwork(nic['ipAddress']).ip))
        return usedips

    def addPublicIPv4IPS(self, subnet, startip, endip, **kwargs):
        """
        Add public ips to an existing range
        """
        if not self.models.publicipv4pool.exists(subnet):
            raise exceptions.NotFound("Could not find PublicIPv4Pool with subnet %s" % subnet)
        try:
            net = netaddr.IPNetwork(subnet)
            if netaddr.IPAddress(startip) not in net:
                raise exceptions.BadRequest("Start IP Addresses %s is not in subnet %s" % (startip, subnet))
            if netaddr.IPAddress(endip) not in net:
                raise exceptions.BadRequest("End IP Addresses %s is not in subnet %s" % (endip, subnet))
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)
        pool = self.models.publicipv4pool.get(subnet)
        pubips = set(pool.pubips)
        newset = {str(ip) for ip in netaddr.IPRange(startip, endip)}
        usedips = self._getUsedIPS(pool)
        duplicateips = usedips.intersection(newset)
        if duplicateips:
            raise exceptions.Conflict("New range overlaps with existing deployed IP Addresses")
        pubips.update(newset)
        pool.pubips = list(pubips)
        self.models.publicipv4pool.set(pool)
        return subnet

    def changeIPv4Gateway(self, subnet, gateway, **kwargs):
        if not self.models.publicipv4pool.exists(subnet):
            raise exceptions.NotFound("Could not find PublicIPv4Pool with subnet %s" % subnet)
        try:
            net = netaddr.IPNetwork(subnet)
            if not checkIPS(net, [gateway]):
                raise exceptions.BadRequest("Gateway Address %s is not in subnet %s" % (gateway, subnet))
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)

        pool = self.models.publicipv4pool.get(subnet)
        pool.gateway = gateway
        self.models.publicipv4pool.set(pool)

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
    def addSize(self, name, vcpus, memory, disksize, **kwargs):
        size = dict()
        size['disk'] = disksize
        size['memory'] = memory
        size['vcpus'] = vcpus
        if self.lcl.size.count(size) >= 1:
            raise exceptions.BadRequest('Size with disk memory vcpu combination already exists.')
        size['name'] = name
        self.lcl.size.set(size)
        self.syncAvailableSizesToCloudbroker()

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
