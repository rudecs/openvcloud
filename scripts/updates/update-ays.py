from JumpScale import j
from optparse import OptionParser
from itertools import ifilter
import multiprocessing
import time
import sys

parser = OptionParser()
parser.add_option("-s", "--self", action="store_true", dest="self", help="only update the update script")
parser.add_option("-r", "--restart", action="store_true", dest="restart", help="only restart everything")
parser.add_option("-R", "--restart-nodes", action="store_true", dest="restartNodes", help="only restart all the nodes")
parser.add_option("-N", "--restart-cloud", action="store_true",
                  dest="restartCloud", help="only restart all the cloudspace vm")
parser.add_option("-u", "--update", action="store_true", dest="update",
                  help="only update git repository, do not restart services")
group = parser.add_option_group('Update version')
group.add_option("--tag-js", dest="tag_js", help="Tag to update JumpScale to")
group.add_option("--tag-ovc", dest="tag_ovc", help="Tag to update OpenvCloud to")
group.add_option("--branch-js", dest="branch_js", help="Branch to update JumpScale to")
group.add_option("--branch-ovc", dest="branch_ovc", help="Branch to update OpenvCloud to")
parser.add_option("-U", "--update-nodes", action="store_true", dest="updateNodes",
                  help="only update node git repository, do not restart services")
parser.add_option("-C", "--update-cloud", action="store_true", dest="updateCloud",
                  help="only update cloudspace git repository, do not restart services")
parser.add_option("-p", "--report", action="store_true", dest="report",
                  help="build a versions log and update git version.md")
parser.add_option("-c", "--commit", action="store_true", dest="commit", help="commit the ovcgit repository")
(options, args) = parser.parse_args()

openvcloud = '/opt/code/github/0-complexity/openvcloud'
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']
nodeprocs = ['redis', 'statsd-collector', 'nginx', 'vncproxy']

# Loading nodes list
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key=lambda x: x.instance)
nodeservices = filter(lambda x: x.instance not in hosts, sshservices)
cloudservices = filter(lambda x: x.instance in hosts, sshservices)


def _get_update_cmd(account, repo, branch, tag):
    cmd = "jscode update -a '%s' -n '%s' -d " % (account, repo)
    if tag:
        cmd += "-t %s" % tag
    elif branch:
        cmd += "-b %s" % branch
    return cmd


def update(nodessh):
    j.console.info('updating host: %s' % nodessh.instance)
    j.remote.cuisine.enableQuiet()
    try:
        nodessh.execute(_get_update_cmd('jumpscale7', '*', options.branch_js, options.tag_js))
        nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'selfhealing', options.branch_ovc, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'g8vdc', options.branch_ovc, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))
    except Exception as e:
        j.console.warning('Failed updating host: %s\n%s' % (nodessh.instance, e))
        sys.exit(1)


def restart(nodessh):
    j.console.info('restarting host\'s services: %s' % nodessh.instance)
    j.remote.cuisine.enableQuiet()
    nodessh.execute('ays stop')
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start')


def restartNode(nodessh):
    j.console.info('restarting (node) host\'s services: %s' % nodessh.instance)
    j.remote.cuisine.enableQuiet()
    for service in nodeprocs:
        nodessh.execute('ays restart -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start -n jsagent')


def stopNode(nodessh):
    j.console.info('stopping (node) host\'s services: %s' % nodessh.instance)
    j.remote.cuisine.enableQuiet()
    for service in nodeprocs:
        nodessh.execute('ays stop -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')


def startNode(nodessh):
    j.console.info('starting (node) host\'s services: %s' % nodessh.instance)
    j.remote.cuisine.enableQuiet()
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
    data = "# Updated on %s\n\n" % time.strftime("%Y-%m-%d, %H:%M:%S")

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
        j.console.warning('Failed to execute on nodes')
        sys.exit(1)


def updateLocal():
    j.console.notice('Updating local system')
    j.do.execute(_get_update_cmd('jumpscale', '*', options.branch_js, options.tag_js))
    j.do.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc, options.tag_ovc))
    j.do.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))


def updateNodes():
    applyOnServices(nodeservices, update)


def updateOpenvcloud(repository):
    j.console.info('Updating local openvcloud repository')
    j.do.execute("cd %s; git pull" % repository)


def updateCloudspace():
    j.console.notice('Updating cloudspace')
    applyOnServices(cloudservices, update)


def restartNodes():
    j.console.notice('restarting nodes')
    applyOnServices(nodeservices, restartNode)


def stopNodes():
    j.console.notice('stopping nodes')
    applyOnServices(nodeservices, stopNode)


def startNodes():
    j.console.notice('starting nodes')
    applyOnServices(nodeservices, startNode)


def restartCloudspace():
    j.console.notice('restarting cloudspace')
    applyOnServices(cloudservices, restart)


def versionBuilder():
    # Updating version file
    j.console.notice('grabbing version')
    j.remote.cuisine.enableQuiet()

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

    j.console.notice('version committed')


def updateGit():
    # get our local repository path
    settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
    repopath = settings.getStr('instance.ovc.path')

    j.system.process.run("cd %s; git add ." % repopath, True, False)
    j.system.process.run("cd %s; git commit -m 'environement updated (update script)'" % repopath, True, False)
    j.system.process.run("cd %s; git push" % repopath, True, False)


"""
Worker stuff
"""

allStep = True

if options.self:
    allStep = False
    j.console.notice('starting self-update')
    updateOpenvcloud(openvcloud)
    j.console.notice('self-update successful')

if options.update:
    allStep = False
    j.console.notice('updating cloudspace and nodes')

    updateLocal()
    updateCloudspace()
    updateNodes()

    j.console.notice('node and cloudspace updated')

if options.updateNodes:
    allStep = False

    j.console.notice('updating all nodes')
    updateNodes()
    j.console.notice('all nodes updated')

if options.updateCloud:
    allStep = False

    j.console.notice('updating cloudspace')

    updateLocal()
    updateCloudspace()

    j.console.notice('cloudspace updated')

if options.restartCloud or options.restart:
    allStep = False

    j.console.notice('restarting cloudspace')
    restartCloudspace()

    j.console.notice('cloudspace restarted')

if options.restartNodes or options.restart:
    allStep = False

    j.console.notice('restarting nodes')

    restartNodes()

    j.console.notice('node restarted')

if options.report:
    allStep = False

    j.console.notice('reporting installed versions')

    versionBuilder()

    j.console.notice('reporting done')

if options.commit:
    allStep = False

    j.console.notice('updating ovcgit repository')

    updateGit()

    j.console.notice('repository up-to-date')

if allStep:
    j.remote.cuisine.enableQuiet()
    j.console.notice('processing complete upgrade')
    starttime = int(time.time())

    updateLocal()
    updateCloudspace()
    updateNodes()
    stopNodes()
    restartCloudspace()
    startNodes()
    j.console.notice('Cleaning logs')
    master = next(ifilter(lambda x: x.instance == 'ovc_master', cloudservices))
    master.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/cleanlogs.py -s {}'.format(starttime))

    versionBuilder()

    j.console.notice('everything done')


j.application.stop()
