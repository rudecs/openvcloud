import netaddr

class Network(object):
    def __init__(self, models):
        self.models = models

    def getPublicIpAddress(self):
        for poolid in self.models.publicipv4pool.list():
            pool = self.models.publicipv4pool.get(poolid)
            if pool.pubips:
                pubip = pool.pubips.pop()
                self.models.publicipv4pool.set(pool)
                net = netaddr.IPNetwork(poolid)
                return netaddr.IPNetwork("%s/%s" % (pubip, net.prefixlen))

    def releasePublicIpAddress(self, publicip):
        net = netaddr.IPNetwork(publicip)
        pool = self.models.publicipv4pool.get(str(net.cidr))
        if not pool:
            return
        pubips = set(pool.pubips)
        pubips.add(str(net.ip))
        pool.pubips = list(pubips)
        self.models.publicipv4pool.set(pool)
