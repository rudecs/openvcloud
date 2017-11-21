from JumpScale import j
from optparse import OptionParser
from itertools import ifilter
import multiprocessing
import time
import sys

CURSORUP = u'\u001b[{n}A'
CLEAREOL = u'\u001b[0K'
COLORESET = u'\u001b[0m'
COLORRED = u'\u001b[31m'
COLORGREEN = u'\u001b[32m'
COLORYELLOW = u'\u001b[33m'
COLORBLUE = u'\u001b[34m'

COLORMAP = {
    'QUEUED': COLORYELLOW,
    'RUNNING': COLORGREEN,
    'DONE': COLORBLUE,
    'ERROR': COLORRED,
}

parser = OptionParser()
parser.add_option("-s", "--self", action="store_true", dest="self", help="only update the update script")
parser.add_option("-r", "--restart", action="store_true", dest="restart", help="only restart everything")
parser.add_option("-R", "--restart-nodes", action="store_true", dest="restartNodes", help="only restart all the nodes")
parser.add_option("-N", "--restart-cloud", action="store_true",
                  dest="restartCloud", help="only restart all the cloudspace vm")

parser.add_option("-n", "--concurrency", type=int, default=0)
parser.add_option("-u", "--update", action="store_true", dest="update",
                  help="only update git repository, do not restart services")
parser.add_option("--noupdate", action="store_true", dest="noupdate",
                  help="if combined with normal update this will only restart services not update them")
parser.add_option("--node", default=None, help="Apply action on this node only")
group = parser.add_option_group('Update version')
group.add_option("--tag-js", dest="tag_js", help="Tag to update JumpScale to")
group.add_option("--tag-ovc", dest="tag_ovc", help="Tag to update OpenvCloud to")
group.add_option("--branch-js", dest="branch_js", help="Branch to update JumpScale to")
group.add_option("--branch-ovc", dest="branch_ovc", help="Branch to update OpenvCloud to")
group.add_option("--branch-ovc-core", dest="branch_ovc_core", default=None, help="Branch to update OpenvCloud to")
group.add_option("--branch-ovc-selfhealing", dest="branch_ovc_selfhealing", default=None, help="Branch to update OpenvCloud to")
parser.add_option("-U", "--update-nodes", action="store_true", dest="updateNodes",
                  help="only update node git repository, do not restart services")
parser.add_option("-C", "--update-cloud", action="store_true", dest="updateCloud",
                  help="only update cloudspace git repository, do not restart services")
parser.add_option("-p", "--report", action="store_true", dest="report",
                  help="build a versions log and update git version.md")
parser.add_option("-c", "--commit", action="store_true", dest="commit", help="commit the ovcgit repository")
(options, args) = parser.parse_args()
if options.branch_ovc_core is None:
    options.branch_ovc_core = options.branch_ovc
if options.branch_ovc_selfhealing is None:
    options.branch_ovc_selfhealing = options.branch_ovc

openvcloud = '/opt/code/github/0-complexity/openvcloud'
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']
nodeprocs = ['redis', 'statsd-collector', 'nginx', 'vncproxy']

# Loading nodes list
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key=lambda x: x.instance)
if options.node:
    sshservices = filter(lambda x: x.instance == options.node, sshservices)
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
    j.remote.cuisine.enableQuiet()
    try:
        nodessh.execute(_get_update_cmd('jumpscale7', '*', options.branch_js, options.tag_js))
        nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc_core, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'selfhealing', options.branch_ovc_selfhealing, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'g8vdc', options.branch_ovc, options.tag_ovc))
        nodessh.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))
    except Exception as e:
        j.console.warning('Failed updating host: %s\n%s' % (nodessh.instance, e))
        sys.exit(1)


def restart(nodessh):
    j.remote.cuisine.enableQuiet()
    nodessh.execute('ays stop')
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start')


def restartNode(nodessh):
    j.remote.cuisine.enableQuiet()
    for service in nodeprocs:
        nodessh.execute('ays restart -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')
    nodessh.execute('ays start -n jsagent')


def stopNode(nodessh):
    j.remote.cuisine.enableQuiet()
    for service in nodeprocs:
        nodessh.execute('ays stop -n %s' % service)
    nodessh.execute('fuser -k 4446/tcp || true')


def startNode(nodessh):
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


def applyOnServices(services, func, msg=None, kwargs=None):
    for service in services:
        service.status = 'QUEUED'
    runningjobs = []
    alljobs = []
    servicestostart = services[:]
    concurrency = options.concurrency or len(services)

    def getStatus(service):
        status = service.status
        if status in COLORMAP:
            status = COLORMAP[status] + status + COLORESET
        return status

    def print_status(up=False):
        if msg:
            if up:
                sys.stdout.write(CURSORUP.format(n=len(services)))
            for service in services:
                status = getStatus(service)
                line = msg + CLEAREOL
                print(line.format(status=status, name=service.instance))

    def schedule_services():
        while len(runningjobs) < concurrency and servicestostart:
            startme = servicestostart.pop(0)
            proc = multiprocessing.Process(target=func, args=(startme,), kwargs=kwargs or {})
            proc.start()
            proc.service = startme
            proc.service.status = 'RUNNING'
            runningjobs.append(proc)
            alljobs.append(proc)
    
    schedule_services()
    print_status()

    while runningjobs:
        time.sleep(1)
        statechange = False
        up = True
        for runningjob in runningjobs[:]:
            if not runningjob.is_alive():
                statechange = True
                runningjobs.remove(runningjob)
                if runningjob.exitcode:
                    up = False
                    runningjob.service.status = 'ERROR'
                else:
                    runningjob.service.status = 'DONE'
        if statechange:
            schedule_services()
            print_status(up)

    error = False
    for job in alljobs:
        job.join()
        if job.exitcode:
            funcname = getattr(func, 'func_name', str(func))
            j.console.warning('Failed to execute {} on {}'.format(funcname, job.service))
            error = True
    if error:
        sys.exit(1)


def updateLocal():
    j.console.notice('Updating local system')
    with j.logger.nostdout():
        j.do.execute(_get_update_cmd('jumpscale', '*', options.branch_js, options.tag_js))
        j.do.execute(_get_update_cmd('0-complexity', 'openvcloud', options.branch_ovc, options.tag_ovc))
        j.do.execute(_get_update_cmd('0-complexity', 'openvcloud_ays', options.branch_ovc, options.tag_ovc))


def updateNodes():
    j.console.notice('Updating all nodes:')
    applyOnServices(nodeservices, update, msg="\t[{status}] {name}")


def updateOpenvcloud(repository):
    j.console.info('Updating local openvcloud repository')
    j.do.execute("cd %s; git pull" % repository)


def updateCloudspace():
    j.console.notice('Updating cloudspace:')
    applyOnServices(cloudservices, update, msg="\t[{status}] {name}")


def restartNodes():
    j.console.notice('Restarting nodes:')
    applyOnServices(nodeservices, restartNode, msg="\t[{status}] {name}")


def cleanupLogs():
    j.console.notice('Cleanup logs')

    def cleanlogs(master):
        master.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/cleanlogs.py -s {}'.format(starttime))
    master = next(ifilter(lambda x: x.instance == 'ovc_master', cloudservices))
    applyOnServices([master], cleanlogs)


def stopNodes():
    j.console.notice('Stopping nodes:')
    applyOnServices(nodeservices, stopNode, msg="\t[{status}] {name}")


def startNodes():
    j.console.notice('Starting nodes:')
    applyOnServices(nodeservices, startNode, msg="\t[{status}] {name}")


def restartCloudspace():
    j.console.notice('Restarting cloudspace:')
    applyOnServices(cloudservices, restart, msg="\t[{status}] {name}")
    for service in j.atyourservice.findServices(name='g8vdc'):
        service.configure()


def versionBuilder():
    # Updating version file
    j.console.notice('Grabbing version')
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

    with j.logger.nostdout():
        j.do.execute("cd %s; git add %s" % (repopath, versionfile))
        j.do.execute("cd %s; git commit -m 'environement updated'" % repopath)
        j.do.execute("cd %s; git push" % repopath)

    j.console.notice('version committed')


def updateGit():
    # get our local repository path
    settings = j.application.getAppInstanceHRD(name='ovc_setup', instance='main', domain='openvcloud')
    repopath = settings.getStr('instance.ovc.path')
    with j.logger.nostdout():
        j.do.execute("cd %s; git add ." % repopath)
        j.do.execute("cd %s; git commit -m 'environement updated (update script)'" % repopath)
        j.do.execute("cd %s; git push" % repopath)


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
    j.console.notice('Updating cloudspace and nodes')

    updateLocal()
    updateCloudspace()
    updateNodes()

if options.updateNodes:
    allStep = False
    updateNodes()

if options.updateCloud:
    allStep = False

    updateLocal()
    updateCloudspace()

if options.restartCloud or options.restart:
    allStep = False
    restartCloudspace()

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

    if not options.noupdate:
        updateLocal()
        updateCloudspace()
        updateNodes()
    stopNodes()
    restartCloudspace()
    startNodes()
    cleanupLogs()

    versionBuilder()

    j.console.notice('everything done')


j.application.stop()
