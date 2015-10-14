from JumpScale import j
import time

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

def header(hostname):
    data  = "## Host: %s\n\n" % hostname
    data += "| Account | Repository | Version (commit) |\n"
    data += "|----|----|----|\n"
    
    return data

# Local update
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)

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


# Updating version file
print '[+] grabbing version'

# get our local repository path
settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
repopath = settings.getStr('instance.ovc.path')

versionfile = '%s/version.md' % repopath
statuscmd = 'jscode status -n "*" | grep lrev: | sed s/lrev://g | awk \'{ printf "| %s | %s | %s |\\n", $1, $2, $9 }\''

# header
data  = "# Updated on %s\n\n" % time.strftime("%Y-%m-%d, %H:%M:%S")
data += header("ovc_git")
output = j.system.process.run(statuscmd, False, True)
data += output[1]
data += "\n"

# grab version
for host in hosts:
    ns = findService(host)
    if ns:
        data += header(host)
        data += ns.execute(statuscmd)
        data += "\n\n"

for ns in sshservices:
    if ns.instance not in hosts:
        data += header(ns.instance)
        data += ns.execute(statuscmd)
        data += "\n\n"

with open(versionfile, 'w') as f:
    f.write(data)

output = j.system.process.run("cd %s; git add %s" % (repopath, versionfile), True, False)
output = j.system.process.run("cd %s; git commit -m 'environement updated'" % repopath, True, False)
output = j.system.process.run("cd %s; git push" % repopath, True, False)

print '[+] update committed'
