from JumpScale import j

locations = {}
for service in j.atyourservice.findServices(name='autossh', instance='http_proxy'):
    location = service.parent.parent.instance
    host = service.hrd.getStr('instance.remote.bind')
    port = service.hrd.getStr('instance.remote.port')
    locations.setdefault(location, []).append('%s:%s' % (host, port))


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
