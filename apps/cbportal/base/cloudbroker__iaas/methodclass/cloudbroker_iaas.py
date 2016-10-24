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

    def addExternalNetwork(self, name, subnet, gateway, startip, endip, gid, vlan, accountId, **kwargs):
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
            if self.models.externalnetwork.count({'vlan': vlan}) > 0:
                raise exceptions.Conflict("VLAN {} is already in use by another external network")
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)

        pool = self.models.externalnetwork.new()
        pool.gid = int(gid)
        pool.gateway = gateway
        pool.name = name
        pool.vlan = vlan
        pool.subnetmask = str(net.netmask)
        pool.network = str(net.network)
        pool.accountId = accountId
        pool.ips = [str(ip) for ip in netaddr.IPRange(startip, endip)]
        pool.id, _, _ = self.models.externalnetwork.set(pool)
        return pool.id

    def getUsedIPInfo(self, pool):
        network = {'spaces': [], 'vms': []}
        for space in self.models.cloudspace.search({'$query': {'gid': pool.gid,
                                                               'externalnetworkId': pool.id,
                                                               'status': 'DEPLOYED'},
                                                    '$fields': ['id', 'name', 'externalnetworkip']})[1:]:
            network['spaces'].append(space)
        for vm in self.models.vmachine.search({'nics.type': 'PUBLIC', 'status': {'$nin': ['ERROR', 'DESTROYED']}})[1:]:
            for nic in vm['nics']:
                if nic['type'] == 'PUBLIC':
                    tagObject = j.core.tags.getObject(nic['params'])
                    if int(tagObject.tags.get('externalnetworkId', 0)) == pool.id:
                        vm['externalnetworkip'] = nic['ipAddress']
                        network['vms'].append(vm)
        return network

    def _getUsedIPS(self, pool):
        networkinfo = self.getUsedIPInfo(pool)
        usedips = set()
        for obj in networkinfo['vms'] + networkinfo['spaces']:
            ip = str(netaddr.IPNetwork(obj['externalnetworkip']).ip)
            usedips.add(ip)
        return usedips

    def addExternalIPS(self, externalnetworkId, startip, endip, **kwargs):
        """
        Add public ips to an existing range
        """
        if not self.models.externalnetwork.exists(externalnetworkId):
            raise exceptions.NotFound("Could not find externel network with id %s" % externalnetworkId)
        pool = self.models.externalnetwork.get(externalnetworkId)
        try:
            net = netaddr.IPNetwork("{}/{}".format(pool.network, pool.subnetmask))
            if netaddr.IPAddress(startip) not in net:
                raise exceptions.BadRequest("Start IP Addresses %s is not in subnet %s" % (startip, net))
            if netaddr.IPAddress(endip) not in net:
                raise exceptions.BadRequest("End IP Addresses %s is not in subnet %s" % (endip, net))
        except netaddr.AddrFormatError as e:
            raise exceptions.BadRequest(e.message)
        ips = set(pool.ips)
        newset = {str(ip) for ip in netaddr.IPRange(startip, endip)}
        usedips = self._getUsedIPS(pool)
        duplicateips = usedips.intersection(newset)
        if duplicateips:
            raise exceptions.Conflict("New range overlaps with existing deployed IP Addresses")
        ips.update(newset)
        pool.ips = list(ips)
        self.models.externalnetwork.set(pool)
        return True

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
        """
        Add a new size to grid location.

        @param name: str name of new size.
        @param vcpus: int  number of vcpus to be used.
        @param memory: int  amount of memory for this size.
        @param disksize: [int] list of disk sizes available.
        """
        size = dict()
        disks = map(int, disksize.split(","))
        size['disks'] = disks
        size['memory'] = memory
        size['vcpus'] = vcpus
        locations = self.models.location.search({"$query": {}, "$fields": ['gid']})
        size['gids'] = [location['gid'] for location in locations[1:]]
        for disk in disks:
            if self.lcl.size.count({"vcpus": vcpus, "memory": memory, "disk": disk}) >= 1:
                raise exceptions.BadRequest('Size with disk memory vcpu combination already exists.')
            for gid in size['gids']:
                name = '%s-%s-%s-%s' % (vcpus, memory, disk, gid)
                self.lcl.size.set({"disk": disk, "memory": memory, "vcpus": vcpus, 'name': name, "gid": gid})
        size['name'] = name
        cloudbroker_size = next(iter(self.models.size.search({"vcpus": vcpus, "memory": memory})[1:]), None)

        if not cloudbroker_size:
            self.models.size.set(size)
        else:
            cloudbroker_size['disks'].extend(disks)
            self.models.size.set(cloudbroker_size)

        return True

    @auth(['level1', 'level2', 'level3'])
    def deleteSize(self, size_id, **kwargs):
        """
        Delete unused size in location.

        @param size_id: int id if size to be deleted.
        """
        cb_size = self.models.size.get(size_id)
        disks = cb_size.disks
        memory = cb_size.memory
        vcpus = cb_size.vcpus
        if self.models.vmachine.count({"sizeId": size_id}) == 0:
            self.models.size.delete(size_id)
            self.lcl.size.deleteSearch({"disk": {"$in": disks}, "memory": memory, "vcpus": vcpus})
        return True


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
