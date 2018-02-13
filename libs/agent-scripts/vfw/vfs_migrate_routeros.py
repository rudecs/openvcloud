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


def action(networkid, sourceip, vlan, externalip):
    from CloudscalerLibcloud.utils.network import Network
    import libvirt
    import netaddr
    from xml.etree import ElementTree
    target_con = libvirt.open()
    try:
        source_con = libvirt.open('qemu+ssh://%s/system' % sourceip)
    except:
        source_con = None
    network = Network()
    hrd = j.atyourservice.get(name='vfwnode', instance='main').hrd
    netrange = hrd.get("instance.vfw.netrange.internal")
    internalip = str(netaddr.IPAddress(netaddr.IPNetwork(netrange).first + int(networkid)))

    createnetwork = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'createnetwork')
    createnetwork.executeLocal(networkid=networkid)
    create_external_network = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'create_external_network')
    create_external_network.executeLocal(vlan=vlan)
    name = 'routeros_%04x' % networkid

    if source_con:
        templatepath = '/var/lib/libvirt/images/routeros/template/'
        destination = '/var/lib/libvirt/images/routeros/{0:04x}'.format(networkid)
        try:
            domain = source_con.lookupByName(name)
        except libvirt.libvirtError:
            domain = None
        if domain:
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                if not j.system.fs.exists(destination):
                    print 'Creating image snapshot %s -> %s' % (templatepath, destination)
                localip = j.system.net.getReachableIpAddress(sourceip, 22)
                targeturl = "tcp://{}".format(localip)
                if not j.system.fs.exists(destination):
                    j.system.btrfs.snapshot(templatepath, destination)
                xmldom = ElementTree.fromstring(domain.XMLDesc())
                seclabel = xmldom.find('seclabel')
                if seclabel is not None:
                    xmldom.remove(seclabel)
                xml = ElementTree.tostring(xmldom)
                flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE | libvirt.VIR_MIGRATE_NON_SHARED_DISK
                try:
                    domain.migrate2(target_con, flags=flags, dxml=xml, uri=targeturl)
                except Exception as e:
                    try:
                        target_domain = target_con.lookupByName(name)
                        target_domain.undefine()
                    except:
                        pass  # vm wasn't created on target
                    raise e
                domain = target_con.lookupByName(name)
                network.protect_external(domain, externalip)
                network.protect_gwmgmt(domain, internalip)
            else:
                domain.undefine()
                return False
        # remove disk from source
        con = j.remote.cuisine.connect(sourceip, 22)
        con.run('btrfs subvol delete {} || true'.format(destination))
        return True
    else:
        # source is not available caller should probable do a restore from scratch
        return False
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--networkid', type=int)
    parser.add_argument('-s', '--sourceip')
    parser.add_argument('-v', '--vlan', type=int, default=0)
    options = parser.parse_args()
    action(options.networkid, options.sourceip, options.vlan)
