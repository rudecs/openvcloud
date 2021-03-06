from JumpScale import j

descr = """
Limit nic speed
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
queue = "default"
async = True


def action(networkId, rate, burst):
    for iface in ['pub', 'spc']:
        pubiface = '%s-%04x' % (iface, networkId)
        if rate:
            j.system.qos.limitNic(pubiface, '%skb' % rate, '%skb' % burst)
        else:
            j.system.qos.removeLimit(pubiface)
