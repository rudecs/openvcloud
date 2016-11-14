from JumpScale import j

descr = """
destroy a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "destroy.routeros"
period = 0  # always in sec
enable = True
async = True
queue = 'hypervisor'


def action(networkid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    import libvirt
    connection = LibvirtUtil()

    con = connection.connection
    bridges = []
    networkidHex = '%04x' % int(networkid)
    name = 'routeros_%s' % networkidHex

    print("CLEANUP: %s/%s" % (networkid, networkidHex))
    dom = None
    try:
        dom = con.lookupByName(name)
        bridges = list(connection._get_domain_bridges(dom))
        dom.destroy()
    except libvirt.libvirtError:
        pass
    if dom is not None:
        try:
            dom.undefine()
        except libvirt.libvirtError:
            pass
    connection.cleanupNetwork(networkid, bridges)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-netid', '--networkid', dest='netid', type=int, help='Network id to delete')
    options = parser.parse_args()
    action(options.netid)
