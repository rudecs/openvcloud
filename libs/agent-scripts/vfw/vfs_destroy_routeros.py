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
    import libvirt
    acl = j.clients.agentcontroller.get()

    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()

    con = connection.connection

    networkidHex = '%04x' % int(networkid)
    name = 'routeros_%s' % networkidHex
    path = '/mnt/vmstor/routeros/{0}/routeros-small-{0}.raw'.format(networkidHex)

    print("CLEANUP: %s/%s" % (networkid, networkidHex))
    try:
        dom = con.lookupByName(name)
        dom.destroy()
        dom.undefine()
    except libvirt.libvirtError:
        pass

    acl.execute('cloudscalers', 'destroyvolume',
                role='storagedriver', gid=j.application.whoAmI.gid,
                args={'path': path})

    connection.cleanupNetwork(networkid)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-netid', '--networkid', dest='netid', type=int, help='Network id to delete')
    options = parser.parse_args()
    action(options.netid)
