from JumpScale import j

descr = """
Upgrade script
* will protect existing external interfaces
* will patch apparmor

"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['cpunode']
async = True


def action():
    from CloudscalerLibcloud.utils.network import Network
    net = Network()
    vcl = j.clients.osis.getNamespace('vfw')
    names = []
    for domain in net.libvirtutil.connection.listAllDomains():
        name = domain.name()
        if 'routeros' not in name:
            continue
        netid = int(name[9:], 16)
        vfwid = '{}_{}'.format(j.application.whoAmI.gid, netid)
        if not vcl.virtualfirewall.exists(vfwid):
            print 'Found orphan ros {}'.format(vfwid)
            continue
        vfw = vcl.virtualfirewall.get(vfwid)
        net.protect_external(domain, vfw.pubips[0])
        names.append(name)
    txt = j.codetools.getTextFileEditor('/etc/apparmor.d/abstractions/libvirt-qemu')
    txt.appendReplaceLine('/sys/devices/system/cpu', '  /sys/devices/system/cpu/** r,')
    txt.save()

    if j.system.platform.ubuntu.serviceExists('apparmor'):
        j.system.platfor.ubuntu.reloadService('apparmor')


    return names


if __name__ == '__main__':
    print(action())
