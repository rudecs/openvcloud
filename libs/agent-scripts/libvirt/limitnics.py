from JumpScale import j

descr = """
Limit nic speed
"""

category = "cloudbroker"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
queue = "default"
async = True


def action(machineids, rate, burst):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    for machineid in machineids:
        domain = connection.get_domain(machineid)
        for nic in list(connection.get_domain_nics(domain['XMLDesc'])):
            if rate:
                j.system.qos.limitNic(nic, '%skb' % rate, '%skb' % burst)
            else:
                j.system.qos.removeLimit(nic)
