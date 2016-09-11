from JumpScale import j

locations = {}
for service in j.atyourservice.findServices(name='autossh', instance='http_proxy'):
    location = service.parent.parent.instance
    host = service.hrd.getStr('instance.remote.bind')
    port = service.hrd.getStr('instance.remote.port')
    locations.setdefault(location, []).append('%s:%s' % (host, port))

for service in j.atyourservice.findServices(name='autossh', instance='http_proxy_ovs'):
    location = service.parent.parent.instance
    host = service.hrd.getStr('instance.remote.bind')
    port = service.hrd.getStr('instance.remote.port')
    locations.setdefault('ovs-' + location, []).append('%s:%s' % (host, port))


# updating proxy service
proxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')

offloader = j.atyourservice.get(name='ssloffloader', parent=proxy)
for location, hosts in locations.iteritems():
    offloader.hrd.set('instance.generated.%s' % location, hosts)
offloader.hrd.save()

print '[+] patching nginx configuration'

# FIXME: better way to reinstall it
proxy.execute('rm -f /opt/jumpscale7/hrd/apps/openvcloud__ssloffloader__main/installed.version')
offloader.consume('node', proxy.instance)
offloader.install(reinstall=True)

# update portal entries
master = j.atyourservice.get(name='node.ssh', instance='ovc_master')
portal = j.atyourservice.get(name='portal', parent=master)
ovs = portal.hrd.getDict('instance.navigationlinks.ovs')
ovs['children'] = 'instance.ovslinks'
ovs['baseurl'] = ovs.get('url') or ovs.get('baseurl')
ovs['url'] = ''
ovslinks = {}
for location in locations.keys():
    ovslinks[location] = ovs['baseurl'] + '/ovcinit/%s' % location

portal.hrd.set('instance.navigationlinks.ovs', ovs)
portal.hrd.set('instance.ovslinks', ovslinks)

master.execute('rm -f /opt/jumpscale7/hrd/apps/jumpscale__portal__main/installed.version')
portal.consume('node', master.instance)
portal.restart()
