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
    nodessh.execute('ays restart -n redis')
    nodessh.execute('ays restart -n statsd-collector')
    nodessh.execute('ays restart -n nginx')
    nodessh.execute('fuser -k 4446/tcp; ays start -n jsagent')
    nodessh.execute('ays restart -n vncproxy')


"""
Markdown stuff
"""
def parse(content):
    hosts = []
    versions = {}
    
    # first: building hosts/repo list
    for host in content:
        hosts.append(host)
        
        for index, line in enumerate(content[host]):
            if line == '':
                del content[host][index]
                continue
            
            item = line.split(',')
            repo = '%s/%s' % (item[0], item[1])
            
            versions[repo] = {}
    
    # building version list
    for host in content:
        for line in content[host]:
            item = line.split(',')
            repo = '%s/%s' % (item[0], item[1])
            commit = item[2][:8]
            
            versions[repo][host] = {'name': commit, 'valid': True}
    
    # checking if version are valid or not
    for version in versions:        
        for hostname in versions[version]:
            for hostmatch in versions[version]:
                # no version for this host
                if hostmatch not in versions[version]:
                    continue
                
                # version mismatch
                if versions[version][hostmatch]['name'] != versions[version][hostname]['name']:
                    versions[version][hostname]['valid'] = False
            
    
    # sorting hosts alphabeticaly
    hosts.sort()
    
    return hosts, versions

def addCellString(value):
    return value + ' | '
    
def addCell(item):
    if not item['valid']:
        return addCellString('**' + item['name'] + '**')
        
    return addCellString(item['name'])

def build(content):
    hosts, versions = parse(content)
    
    # building header
    data  = "# Updated on %s\n\n" % time.strftime("%Y-%m-%d, %H:%M:%S")
    
    data += "| Repository | " + ' | '.join(hosts) + " |\n"
    data += "|" + ("----|" * (len(hosts) + 1)) + "\n"
    
    for repo in versions:
        data += '| ' + addCellString(repo)
        
        for host in hosts:
            if host in versions[repo]:
                data += addCell(versions[repo][host])
            else:
                data += addCellString('')
        
        data += "\n"
    
    return data

"""
Update stuff
"""
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
statuscmd = 'jscode status -n "*" | grep lrev: | sed s/lrev://g | awk \'{ printf "%s,%s,%s\\n", $1, $2, $9 }\''

content = {}

output = j.system.process.run(statuscmd, False, True)
content['ovc_git'] = output[1].split("\n")

# grab version
for host in hosts:
    ns = findService(host)
    if ns:
        content[host] = ns.execute(statuscmd).split("\r\n")

for ns in sshservices:
    if ns.instance not in hosts:
        content[ns.instance] = ns.execute(statuscmd).split("\r\n")

data = build(content)

"""
Append old version
"""

data += "\n\n\n"

for host in content:
    data += "## %s\n\n" % host
    data += "| Repository | Version (commit) |\n"
    data += "|----|----|\n"
    
    
    for line in content[host]:
        items = line.split(',')
        repo = '%s/%s' % (items[0], items[1])
        data += "| %s | %s |\n" % (repo, items[2])
    
    data += "\n\n"

with open(versionfile, 'w') as f:
    f.write(data)

output = j.system.process.run("cd %s; git add %s" % (repopath, versionfile), True, False)
output = j.system.process.run("cd %s; git commit -m 'environement updated'" % repopath, True, False)
output = j.system.process.run("cd %s; git push" % repopath, True, False)

print '[+] update committed'
