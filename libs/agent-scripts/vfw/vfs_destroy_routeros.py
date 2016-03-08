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
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()

    con = connection.connection

    networkidHex = '%04x' % int(networkid)
    networkname = "space_%s"  % networkidHex
    name = 'routeros_%s' % networkidHex
    destinationdir = '/mnt/vmstor/routeros/%s' % networkidHex


    print "CLEANUP: %s/%s"%(networkid,networkidHex)
    try:
        dom = con.lookupByName(name)
        dom.destroy()
        dom.undefine()
    except libvirt.libvirtError:
        pass
    j.system.fs.removeDirTree(destinationdir)
    connection.cleanupNetwork(networkid)
