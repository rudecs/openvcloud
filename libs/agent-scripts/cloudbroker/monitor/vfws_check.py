from JumpScale import j

descr = """
Checks whether vfw can reach its gw
"""

organization = 'jumpscale'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.vfw"

enable = True
async = True
log = False
roles = ['fw',]
queue = 'process'

def action(location):
    import JumpScale.grid.osis
    import netaddr
    import JumpScale.lib.routeros

    osiscl = j.core.osis.getClient(user='root')
    vfwcl = j.core.osis.getClientForCategory(osiscl, 'vfw', 'virtualfirewall')
    cloudspacecl = j.core.osis.getClientForCategory(osiscl, 'cloudbroker', 'cloudspace')
    ROUTEROS_PASSWORD = j.application.config.get('vfw.admin.passwd')
    cidders = j.application.config.getDict('vfw.public.cidrs')
    gws = j.application.config.getDict('vfw.public.gw')

    networks = []
    for c in cidders:
        networks.append(netaddr.IPNetwork('%s/%s' % (c, cidders[c])))

    def getDefaultGW(publicip):
        ipaddress = netaddr.IPAddress(publicip)
        subnet = None
        for net in networks:
            if ipaddress in net:
                subnet = str(net.network)
        if not subnet:
            return None
        return gws[subnet]

    result = dict()
    def chunks(l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i+n]
    def processCloudSpace(cloudspace):
        if cloudspace['status'] != 'DESTROYED':
            status = {'status': False, 'message':'UNKOWN'}
            result[cloudspace['id']] = status
            if cloudspace['networkId']:
                gwip = getDefaultGW(cloudspace['publicipaddress'])
                try:
                    vfw = vfwcl.get("%s_%s" % (j.application.whoAmI.gid, cloudspace['networkId']))
                    if j.system.net.tcpPortConnectionTest(vfw.host, 8728, 7):
                        routeros = j.clients.routeros.get(vfw.host, 'vscalers', ROUTEROS_PASSWORD)
                    else:
                        status['message'] = 'Could not connect to routeros %s' % vfw.host
                        return
                except Exception, e:
                    status['message'] = str(e)
                    return
                if gwip:
                    pingable = routeros.ping(gwip)
                    if pingable:
                        status['status'] = True
                        status['message'] = 'OK'
                    else:
                        status['message'] = 'Could not ping %s'  % gwip
                else:
                    status['message'] = 'No GW assigned'
    for cloudspaces in chunks(cloudspacecl.simpleSearch({'location': location}), 5):
        for cloudspace in cloudspaces:
            print "Checking CoudspaceId: %(id)s NetworkId: %(networkId)s PUBIP: %(publicipaddress)s" % cloudspace
            processCloudSpace(cloudspace)
    return result


if __name__ == '__main__':
    result = action('ca1')
    import yaml
    import json
    with open('/root/vfws_check.json', 'w') as fd:
        json.dump(result, fd)
    print yaml.dump(result)
