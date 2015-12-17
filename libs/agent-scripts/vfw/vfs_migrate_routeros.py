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

def action(networkid, sourceip):
    import libvirt
    BACKPLANE = 'vxbackend'
    nc = j.system.ovsnetconfig
    target_con = libvirt.open()
    source_con = libvirt.open('qemu+ssh://%s/system' % sourceip)

    networkidHex = '%04x' % int(networkid)
    networkname = "space_%s" % networkidHex
    name = 'routeros_%s' % networkidHex

    # setup network vxlan
    nc.ensureVXNet(int(networkid), BACKPLANE)
    xml = '''  <network>
    <name>%(networkname)s</name>
    <forward mode="bridge"/>
    <bridge name='%(networkname)s'/>
     <virtualport type='openvswitch'/>
 </network>''' % {'networkname': networkname}
    try:
        target_con.networkLookupByName(networkname)
    except:
        private = target_con.networkDefineXML(xml)
        private.create()
        private.setAutostart(True)

    domain = source_con.lookupByName(name)
    target_con.defineXML(domain.XMLDesc())

    if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
        flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE
        try:
            domain.migrate2(target_con, flags=flags)
        except:
            try:
                target_domain = target_con.lookupByName(name)
                target_domain.undefine()
            except:
                pass  # vm wasn't created on target
            raise
    else:
        domain.undefine()

    return True


