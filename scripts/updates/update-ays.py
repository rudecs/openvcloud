from JumpScale import j
from optparse import OptionParser
import multiprocessing
import time
import sys

parser = OptionParser()
parser.add_option("-s", "--self", action="store_true", dest="self", help="only update the update script")
parser.add_option("-r", "--restart", action="store_true", dest="restart", help="only restart everything")
parser.add_option("-R", "--restart-nodes", action="store_true", dest="restartNodes", help="only restart all the nodes")
parser.add_option("-N", "--restart-cloud", action="store_true", dest="restartCloud", help="only restart all the cloudspace vm")
parser.add_option("-u", "--update", action="store_true", dest="update", help="only update git repository, do not restart services")
group = parser.add_option_group('Update version')
group.add_option("--tag-js", dest="tag_js", help="Tag to update JumpScale to")
group.add_option("--tag-ovc", dest="tag_ovc", help="Tag to update OpenvCloud to")
group.add_option("--branch-js", dest="branch_js", help="Branch to update JumpScale to")
group.add_option("--branch-ovc", dest="branch_ovc", help="Branch to update OpenvCloud to")
parser.add_option("-U", "--update-nodes", action="store_true", dest="updateNodes", help="only update node git repository, do not restart services")
parser.add_option("-C", "--update-cloud", action="store_true", dest="updateCloud", help="only update cloudspace git repository, do not restart services")
parser.add_option("-p", "--report", action="store_true", dest="report", help="build a versions log and update git version.md")
parser.add_option("-c", "--commit", action="store_true", dest="commit", help="commit the ovcgit repository")
(options, args) = parser.parse_args()

openvcloud = '/opt/code/git/0-complexity/openvcloud'
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']
nodeprocs = ['redis', 'statsd-collector', 'nginx', 'vncproxy']

# Loading nodes list
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)
nodeservices = filter(lambda x:x.instance not in hosts, sshservices)
cloudservices = filter(lambda x:x.instance in hosts, sshservices)

def _get_update_cmd(account, repo, branch, tag):
    cmd = "jscode update -a '%s' -n '%s' -d " % (account, repo)
    if tag:
        cmd += "-t %s" % tag
    elif branch:
        cmd += "-b %s" % branch
    return cmd

def update(nodessh):
    print '[+] updating host: %s' % nodessh.instance
    nodessh.execute(_get_update_cmd('jumpscale7', '*', options.branch_js, options.tag_js))
    nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc, options.tag_ovc))
    nodessh.execute(_get_update_cmd('0-complexity', 'selfhealing', options.branch_ovc, options.tag_ovc))
    nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))

def restart(nodessh):
    print '[+] restarting host\'s services: %s' % nodessh.instance
    nodessh.execute('ays stop')
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start')

def restartNode(nodessh):
    print '[+] restarting (node) host\'s services: %s' % nodessh.instance
    for service in nodeprocs:
        nodessh.execute('ays restart -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start -n jsagent')

def stopNode(nodessh):
    print '[+] stopping (node) host\'s services: %s' % nodessh.instance
    for service in nodeprocs:
        nodessh.execute('ays stop -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')

def startNode(nodessh):
    print '[+] starting (node) host\'s services: %s' % nodessh.instance
    for service in nodeprocs:
        nodessh.execute('ays start -n %s' % service)
    nodessh.execute('ays start -n jsagent')


"""
Markdown stuff
"""
def parse(content):
    hosts = []
    versions = {}

    # first: building hosts/repo list
    for host, lines in content.items():
        hosts.append(host)

        for index, line in enumerate(lines):
            if line == '':
                del content[host][index]
                continue

            item = line.split(',')
            repo = '%s/%s' % (item[0], item[1])

            versions[repo] = {}

    # building version list
    for host, lines in content.items():
        for line in lines:
            item = line.split(',')
            if len(item) < 2:
                continue
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
Updater stuff
"""
def applyOnServices(services, func, kwargs=None):
    procs = list()
    for service in services:
        kwargs = kwargs or {}
        proc = multiprocessing.Process(target=func, args=(service,), kwargs=kwargs)
        proc.start()
        procs.append(proc)
    error = False
    for proc in procs:
        proc.join()
        if proc.exitcode:
            error = True
    if error:
        print 'Failed to execute on nodes'
        sys.exit(1)

def updateLocal():
    print '[+] Updating local system'
    j.do.execute(_get_update_cmd('jumpscale', '*', options.branch_js, options.tag_js))
    j.do.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc, options.tag_ovc))
    j.do.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))

def updateNodes():
    applyOnServices(nodeservices, update)

def updateOpenvcloud(repository):
    print '[+] Updating local openvcloud repository'
    j.do.execute("cd %s; git pull" % repository)

def updateCloudspace():
    print ''
    print '[+] updating cloudspace'
    print ''
    applyOnServices(cloudservices, update)

def restartNodes():
    print ''
    print '[+] restarting nodes'
    print ''
    applyOnServices(nodeservices, restartNode)

def stopNodes():
    print ''
    print '[+] stopping nodes'
    print ''
    applyOnServices(nodeservices, stopNode)

def startNodes():
    print ''
    print '[+] starting nodes'
    print ''
    applyOnServices(nodeservices, startNode)

def restartCloudspace():
    print ''
    print '[+] restarting cloudspace'
    print ''
    applyOnServices(cloudservices, restart)

def versionBuilder():
    # Updating version file
    print '[+] grabbing version'

    # get our local repository path
    settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
    repopath = settings.getStr('instance.ovc.path')

    versionfile = '%s/version.md' % repopath
    statuscmd = 'jscode status -n "*" | grep lrev: | sed s/lrev://g | awk \'{ printf "%s,%s,%s\\n", $1, $2, $9 }\''

    manager = multiprocessing.Manager()
    content = manager.dict()

    output = j.system.process.run(statuscmd, False, True)
    content['ovc_git'] = output[1].split("\n")

    def executeStatus(sshservice, content):
        content[sshservice.instance] = sshservice.execute(statuscmd).split('\r\n')

    # grab version
    applyOnServices(sshservices, executeStatus, kwargs={'content': content})

    data = build(content)

    """
    Append old version
    """

    data += "\n\n\n"

    for host, lines in content.items():
        data += "## %s\n\n" % host
        data += "| Repository | Version (commit) |\n"
        data += "|----|----|\n"


        for line in lines:
            items = line.split(',')
            if len(items) < 2:
                continue
            repo = '%s/%s' % (items[0], items[1])
            data += "| %s | %s |\n" % (repo, items[2])

        data += "\n\n"

    with open(versionfile, 'w') as f:
        f.write(data)

    output = j.system.process.run("cd %s; git add %s" % (repopath, versionfile), True, False)
    output = j.system.process.run("cd %s; git commit -m 'environement updated'" % repopath, True, False)
    output = j.system.process.run("cd %s; git push" % repopath, True, False)

    print '[+] version committed'

def updateGit():
    # get our local repository path
    settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
    repopath = settings.getStr('instance.ovc.path')

    output = j.system.process.run("cd %s; git add ." % repopath, True, False)
    output = j.system.process.run("cd %s; git commit -m 'environement updated (update script)'" % repopath, True, False)
    output = j.system.process.run("cd %s; git push" % repopath, True, False)


"""
Worker stuff
"""

allStep = True

if options.self:
    allStep = False

    print '[+] starting self-update'

    updateOpenvcloud(openvcloud)

    print '[ ]'
    print '[+] self-update successful'
    print '[ ]'

if options.update:
    allStep = False

    print '[+] updating cloudspace and nodes'

    updateLocal()
    updateCloudspace()
    updateNodes()

    print '[ ]'
    print '[+] node and cloudspace updated'
    print '[ ]'

if options.updateNodes:
    allStep = False

    print '[+] updating all nodes'

    updateNodes()

    print '[ ]'
    print '[+] all nodes updated'
    print '[ ]'

if options.updateCloud:
    allStep = False

    print '[+] updating cloudspace'

    updateLocal()
    updateCloudspace()

    print '[ ]'
    print '[+] cloudspace updated'
    print '[ ]'

if options.restartCloud or options.restart:
    allStep = False

    print '[+] restarting cloudspace'

    restartCloudspace()

    print '[ ]'
    print '[+] cloudspace restarted'
    print '[ ]'

if options.restartNodes or options.restart:
    allStep = False

    print '[+] restarting nodes'

    restartNodes()

    print '[ ]'
    print '[+] node restarted'
    print '[ ]'

if options.report:
    allStep = False

    print '[+] reporting installed versions'

    versionBuilder()

    print '[ ]'
    print '[+] reporting done'
    print '[ ]'

if options.commit:
    allStep = False

    print '[+] updating ovcgit repository'

    updateGit()

    print '[ ]'
    print '[+] repository up-to-date'
    print '[ ]'

if allStep:
    print '[+] processing complete upgrade'

    updateLocal()
    updateCloudspace()
    updateNodes()
    stopNodes()
    restartCloudspace()
    startNodes()
    versionBuilder()

    print '[ ]'
    print '[+] everything done'
    print '[ ]'


j.application.stop()
