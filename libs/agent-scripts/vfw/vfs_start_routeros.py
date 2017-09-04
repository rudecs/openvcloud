from JumpScale import j

descr = """
create and start a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
enable = True
async = True
queue = 'hypervisor'


def action(networkid, vlan):
    import os
    createnetwork = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'createnetwork')
    createnetwork.executeLocal(networkid=networkid)
    create_external_network = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'create_external_network')
    bridgename = create_external_network.executeLocal(vlan=vlan)
    import libvirt
    con = libvirt.open()
    try:
        networkidHex = '%04x' % int(networkid)
        name = 'routeros_%s' % networkidHex
        try:
            domain = con.lookupByName(name)
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                return True
            else:
                domain.create()
                return True
        except:
            import jinja2
            networkidHex = '%04x' % int(networkid)
            imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros/template/')
            xmltemplate = jinja2.Template(j.system.fs.fileGetContents(
                j.system.fs.joinPaths(imagedir, 'routeros-template.xml')))

            destination = '/var/lib/libvirt/images/routeros/%s' % networkidHex
            destinationfile = os.path.join(destination, 'routeros.qcow2')
            xmlsource = xmltemplate.render(networkid=networkidHex,
                                           destinationfile=destinationfile,
                                           publicbridge=bridgename)

            dom = con.defineXML(xmlsource)
            dom.create()
            return True
    finally:
        con.close()
    return True
