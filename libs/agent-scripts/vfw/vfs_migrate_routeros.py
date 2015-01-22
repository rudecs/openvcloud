from JumpScale import j

descr = """
move vfw
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
period = 0  # always in sec
enable = True
async = True
queue = 'hypervisor'

def action(networkid, sourceip, targetip, sshkey):
    import JumpScale.lib.routeros
    import JumpScale.baselib.remote
    import libvirt
    import JumpScale.lib.ovsnetconfig

    BACKPLANE = 'vxbackend'
    nc = j.system.ovsnetconfig
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

    try:
        #setup network vxlan
        nc.ensureVXNet(int(networkid), BACKPLANE)
        xml = '''  <network>
        <name>%(networkname)s</name>
        <forward mode="bridge"/>
        <bridge name='%(networkname)s'/>
         <virtualport type='openvswitch'/>
     </network>''' % {'networkname': networkname}
        private = con.networkDefineXML(xml)
        private.create()
        private.setAutostart(True)

        j.system.fs.createDir(destinationdir)
        destinationfile = 'routeros-small-%s.qcow2' % networkidHex
        destinationfile = j.system.fs.joinPaths(destinationdir, destinationfile)
        imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros_template/routeros_template_backup')
        imagefile = j.system.fs.joinPaths(imagedir, 'routeros-small-NETWORK-ID.qcow2')
        j.system.fs.copyFile(imagefile, destinationfile)


        capi = j.remote.cuisine.connect(sourceip, 22)
        if sshkey:
            capi.fabric.api.env['key'] = sshkey
        capi.fabric.api.env['forward_agent'] = True

        xml = capi.run('virsh dumpxml %s' % name)

        try:
            con.defineXML(xml)
        except libvirt.libvirtError, e:
            cleanup()
            raise RuntimeError("Could not create VFW vm from template, network id:%s:%s\n%s"%(networkid,networkidHex,e))

        capi.run('virsh migrate --live %s qemu+ssh://%s/system --copy-storage-inc --verbose --persistent --undefinesource' % (name, targetip))
        capi.run('rm -rf %s' % destinationdir)


    except:
        cleanup()
        raise

    return True


