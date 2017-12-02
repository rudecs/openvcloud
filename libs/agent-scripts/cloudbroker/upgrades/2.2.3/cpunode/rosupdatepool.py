from JumpScale import j

descr = """
Upgrade script
* will remove dhcp pool

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
    import socket
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
        j.console.info('Updating pools on {}'.format(vfwid))
        try:
            ros = j.clients.routeros.get(vfw.host, vfw.username, vfw.password)
        except socket.error:
            j.console.warning('Failed to connect restarting {}'.format(vfwid))
            domain.destroy()
            domain.create()
            if not j.system.net.waitConnectionTest(vfw.host, 8728, timeout=30):
                raise RuntimeError("Failed to get connection to api")
            ros = j.clients.routeros.get(vfw.host, vfw.username, vfw.password)
        try:
            ros.executeScript('/ip dhcp-server set [ /ip dhcp-server find name=server1 ] address-pool=static-only')
            ros.executeScript('/ip pool remove [ /ip pool find name=dhcp ]')
        finally:
            ros.close()
        names.append(name)

    return names


if __name__ == '__main__':
    print(action())
