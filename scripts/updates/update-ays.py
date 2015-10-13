from JumpScale import j

def update(nodessh):
    print ''
    print '[+] updating host: %s' % nodessh.instance
    print ''
    nodessh.execute("jscode update -n '*' -d")

def restart(nodessh):
    print ''
    print '[+] restarting host\'s services: %s' % nodessh.instance
    print ''
    nodessh.execute('ays restart')

# Local update
sshservices = j.atyourservice.findServices(name='node.ssh')

def findService(name):
    for ns in sshservices:
        if ns.instance == name:
            return ns

print '[+] Updating local system'
j.do.execute("jscode update -d -n '*'")

"""
Note: Warning, do not try to do a 'ays restart' on ovcgit
"""

# Remote update

hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

print '[+] Updating system'

for host in hosts:
    ns = findService(host)
    if ns:
        update(ns)

for host in hosts:
    ns = findService(host)
    if ns:
        restart(ns)

print '[+] Updating nodes'
for ns in sshservices:
    if ns.instance not in hosts:
        update(ns)

print '[+] Restarting nodes services'
for ns in sshservices:
    if ns.instance not in hosts:
        restart(ns)


print '[+] update completed'
