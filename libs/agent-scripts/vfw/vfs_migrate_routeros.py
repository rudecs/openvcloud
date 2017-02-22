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


def action(networkid, sourceip, vlan):
    import libvirt
    target_con = libvirt.open()
    try:
        source_con = libvirt.open('qemu+ssh://%s/system' % sourceip)
    except:
        source_con = None

    createnetwork = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'createnetwork')
    createnetwork.executeLocal(networkid=networkid)
    create_external_network = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'create_external_network')
    create_external_network.executeLocal(vlan=vlan)
    name = 'routeros_%04x' % networkid

    if source_con:
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
    else:
        import jinja2
        acl = j.clients.agentcontroller.get()
        devicename = 'routeros/{0}/routeros-small-{0}'.format(networkidHex)
        edgeip, edgeport, edgetransport = acl.execute(
            'greenitglobe', 'getedgeconnection', role='storagedriver', gid=j.application.whoAmI.gid)
        imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros/template/')
        xmltemplate = jinja2.Template(j.system.fs.fileGetContents(
            j.system.fs.joinPaths(imagedir, 'routeros-template.xml')))
        xmlsource = xmltemplate.render(networkid=networkidHex, name=devicename,
                                       edgehost=edgeip, edgeport=edgeport,
                                       edgetransport=edgetransport)
        dom = target_con.defineXML(xmlsource)
        dom.create()

    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--networkid', type=int)
    parser.add_argument('-s', '--sourceip')
    parser.add_argument('-v', '--vlan', type=int, default=0)
    options = parser.parse_args()
    action(options.networkid, options.sourceip, options.vlan)
