from JumpScale import j

# building nodes list
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)

roothosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

nodes = []
hosts = []

for ns in sshservices:
	if ns.instance not in roothosts:
		nodes.append(ns)

# dump
print '[+] nodes found: %d' % len(nodes)

for node in nodes:
	host = node.hrd.getStr('instance.ip')
	port = node.hrd.getStr('instance.ssh.port')
	
	print '[+] %s: %s:%s' % (node.instance, host, port)
	
	remote = 'server %s:%s;' % (host, port)
	hosts.append(remote)

if len(hosts) == 0:
	print '[-] no nodes found'
	j.application.stop()

# building defense and novnc server list
novnc = "\n\t".join(hosts)
defense = "\n\t".join(hosts)
ovs = "\n\t".join(hosts[:3])

# updating proxy service
proxy = j.atyourservice.get(name='node.ssh', instance='ovc_proxy')
offloader = j.atyourservice.get(name='ssloffloader', parent=proxy)

print novnc
offloader.hrd.set('instance.generated.novnc', novnc)
offloader.hrd.set('instance.generated.defense', defense)
offloader.hrd.set('instance.generated.ovs', ovs)

print offloader.hrd
