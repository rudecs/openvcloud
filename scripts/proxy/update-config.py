from JumpScale import j

# building nodes list
openvcloud = j.clients.openvcloud.get()
nodes = openvcloud.getRemoteNodes()
hosts = []

# dump
print '[+] nodes found: %d' % len(nodes)

for node in nodes:
	# if nginx is installed, this is a good node for list
	cpunode = j.atyourservice.findServices(name='nginx', parent=node)
	
	if len(cpunode) < 1:
		continue
	
	host = node.hrd.getStr('instance.ip')
	port = 2001 # FIXME: variable ?
	
	print '[+] %s: %s:%s' % (node.instance, host, port)
	
	remote = 'server %s:%s;' % (host, port)
	hosts.append(remote)

if len(hosts) == 0:
	print '[-] no nodes found'
	j.application.stop()

# building defense and novnc server list
delimiter = "           \n"
novnc = delimiter.join(hosts)
defense = delimiter.join(hosts)
ovs = delimiter.join(hosts[:3])

# updating proxy service
proxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
offloader = j.atyourservice.get(name='ssloffloader', parent=proxy)

offloader.hrd.set('instance.generated.novnc', novnc)
offloader.hrd.set('instance.generated.defense', defense)
offloader.hrd.set('instance.generated.ovs', ovs)
offloader.hrd.save()

print '[+] patching nginx configuration'

# FIXME: better way to reinstall it
proxy.execute('rm -f /opt/jumpscale7/hrd/apps/openvcloud__ssloffloader__main/installed.version')
offloader.consume('node', proxy.instance)
offloader.install(reinstall=True)
