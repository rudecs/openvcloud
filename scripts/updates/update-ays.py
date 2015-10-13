from JumpScale import j

# Local update

print '[+] updating local system'
j.do.execute("jscode update -d -n '*'")

"""
Note: Warning, do not try to do a 'ays restart' on ovcgit
"""

# Remote update

hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

print '[+] updating system'

for host in hosts:
	print ''
	print '[+] updating host: %s' % host
	print ''
	ns = j.atyourservice.get(name='node.ssh', instance=host)
	ns.execute("jscode update -n '*' -d")

for host in hosts:
	print ''
	print '[+] restarting host: %s' % host
	print ''
	ns = j.atyourservice.get(name='node.ssh', instance=host)
	ns.execute('ays restart')

print '[+] update completed'
