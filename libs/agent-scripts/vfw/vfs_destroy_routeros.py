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

    con = libvirt.open()

    j.packages.findNewest('', 'routeros_config').install()

    networkidHex = '%04x' % int(networkid)
    networkname = "space_%s"  % networkidHex
    name = 'routeros_%s' % networkidHex
    destinationdir = '/mnt/vmstor/routeros/%s' % networkidHex


    def cleanup():
        print "CLEANUP: %s/%s"%(networkid,networkidHex)
        try:
            dom = con.lookupByName(name)
            dom.destroy()
            dom.undefine()
        except libvirt.libvirtError:
            pass
        j.system.fs.removeDirTree(destinationdir)
        def deleteNet(net):
            try:
                net.destroy()
            except:
                pass
            try:
                net.undefine()
            except:
                pass
        try:
            for net in con.listAllNetworks():
                if net.name() == networkname:
                    deleteNet(net)
                    break
        except:
            pass

    cleanup()

