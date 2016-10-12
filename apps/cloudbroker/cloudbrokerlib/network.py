import netaddr


class Network(object):
    def __init__(self, models):
        self.models = models

    def getExternalIpAddress(self, gid, externalnetworkId=None):
        with self.models.externalnetwork.lock(str(gid)):
            query = {'gid': gid}
            if externalnetworkId is not None:
                query['id'] = externalnetworkId
            for pool in self.models.externalnetwork.search(query)[1:]:
                if pool['ips']:
                    pool = self.models.externalnetwork.get(pool['id'])
                    ip = pool.ips.pop(0)
                    self.models.externalnetwork.set(pool)
                    return pool, netaddr.IPNetwork("%s/%s" % (ip, pool.subnetmask))

    def releaseExternalIpAddress(self, externalnetworkId, ip):
        net = netaddr.IPNetwork(ip)
        try:
            pool = self.models.externalnetwork.get(externalnetworkId)
        except:
            pool = None
        if not pool:
            return
        with self.models.externalnetwork.lock(str(pool.gid)):
            ips = set(pool.ips)
            ips.add(str(net.ip))
            pool.ips = list(ips)
            self.models.externalnetwork.set(pool)
