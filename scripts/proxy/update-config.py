from JumpScale import j

upstreams = {}
locations = set()

refsrv = j.atyourservice.findServices(name='node.ssh', instance='ovc_reflector')
if len(refsrv) == 0:
    j.console.notice('Searching for nginx services')
    for service in j.atyourservice.findServices(name='node.ssh'):
        if service.parent is None:
            # skip nodes that dont have parents
            continue
        nginxservices = service.execute('ls /opt/nginx/cfg/sites-enabled/; exit 0')
        ovsservice = 'storagedriver_aio' in nginxservices
        cpuservice = 'cpunode_aio' in nginxservices
        envname = service.parent.instance

        if ovsservice or cpuservice:
            host = service.hrd.getStr('instance.ip')
            port = "2001"  # assume there is no reflector
            locations.add(envname)
            if ovsservice:
                j.console.info('Adding ovs {} {}'.format(service.instance, envname))
                upstreams.setdefault('ovs-' + envname, []).append('%s:%s' % (host, port))
            if cpuservice:
                j.console.info('Adding cpu {} {}'.format(service.instance, envname))
                upstreams.setdefault(envname, []).append('%s:%s' % (host, port))

else:
    j.console.notice('Searching for http proxies')
    for service in j.atyourservice.findServices(name='autossh', instance='http_proxy'):
        location = service.parent.parent.instance
        host = service.hrd.getStr('instance.remote.bind')
        port = service.hrd.getStr('instance.remote.port')
        upstreams.setdefault(location, []).append('%s:%s' % (host, port))
        locations.add(location)

    for service in j.atyourservice.findServices(name='autossh', instance='http_proxy_ovs'):
        location = service.parent.parent.instance
        host = service.hrd.getStr('instance.remote.bind')
        port = service.hrd.getStr('instance.remote.port')
        upstreams.setdefault('ovs-' + location, []).append('%s:%s' % (host, port))
        locations.add(location)

# updating proxy service
proxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')

offloader = j.atyourservice.get(name='ssloffloader', parent=proxy)
for location, hosts in upstreams.iteritems():
    offloader.hrd.set('instance.generated.%s' % location, hosts)
offloader.hrd.save()

j.console.notice('Patching nginx configuration')

# FIXME: better way to reinstall it
proxy.execute('rm -f /opt/jumpscale7/hrd/apps/openvcloud__ssloffloader__main/installed.version')
offloader.consume('node', proxy.instance)
offloader.install(reinstall=True)

# update portal entries
j.console.notice('Updating portal config')
masteraioconfig = j.application.getAppInstanceHRD(name='cb_master_aio', instance='main', domain='openvcloud')
baseurl = masteraioconfig.get('instance.param.ovs.url')
master = j.atyourservice.get(name='node.ssh', instance='ovc_master')
portal = j.atyourservice.get(name='portal', parent=master)
ovs = portal.hrd.getDict('instance.navigationlinks.ovs')
ovs['external'] = 'blank'
if len(locations) == 1:
    ovs.pop('children', None)
    ovs['url'] = baseurl + '/ovcinit/%s' % list(locations)[0]
else:
    ovs['children'] = 'instance.ovslinks'
    ovs['url'] = ''
    ovslinks = {}
    for location in locations:
        ovslinks[location] = baseurl + '/ovcinit/%s' % location
    portal.hrd.set('instance.ovslinks', ovslinks)

portal.hrd.set('instance.navigationlinks.ovs', ovs)

master.execute('rm -f /opt/jumpscale7/hrd/apps/jumpscale__portal__main/installed.version')
portal.consume('node', master.instance)
portal.restart()
