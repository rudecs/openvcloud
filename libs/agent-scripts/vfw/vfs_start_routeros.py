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


def action(fwobject):
    import os
    import libvirt
    from CloudscalerLibcloud.utils.network import Network
    internalip = fwobject['host']
    networkid = fwobject['id']
    vlan = fwobject['vlan']

    def createnetwork():
        createnetwork = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'createnetwork')
        createnetwork.executeLocal(networkid=networkid)
        create_external_network = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'create_external_network')
        return create_external_network.executeLocal(vlan=vlan)

    def protect_interfaces(network, domain):
        for publicip in fwobject['pubips']:
            network.protect_external(domain, publicip)
        network.protect_gwmgmt(domain, internalip)


    network = Network()
    con = network.libvirtutil.connection
    try:
        networkidHex = '%04x' % int(networkid)
        name = 'routeros_%s' % networkidHex
        try:
            domain = con.lookupByName(name)
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                return True
            else:
                createnetwork()
                domain.create()
                protect_interfaces(network, domain)
                return True
        except:
            bridgename = createnetwork()
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
            protect_interfaces(network, domain)
            return True
    finally:
        network.close()
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--network-id', dest='networkid', required=True)
    parser.add_argument('-v', '--vlan', type=int, required=True)
    args = parser.parse_args()
    action(args.networkid, args.vlan)
