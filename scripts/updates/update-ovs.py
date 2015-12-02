from JumpScale import j
from optparse import OptionParser
import time
import json

parser = OptionParser()
parser.add_option("-c", "--check", action="store_true", dest="check", help="check for update")
parser.add_option("-u", "--update", action="store_true", dest="update", help="just run apt-get update on each nodes")
parser.add_option("-P", "--preprocess", action="store_true", dest="prepro", help="runs some pre-upgrade commands")
parser.add_option("-S", "--postprocess", action="store_true", dest="postpro", help="runs some post-upgrade commands")
parser.add_option("-r", "--arakoon", action="store_true", dest="arakoon", help="attempt to update only arakoon")
parser.add_option("-o", "--framework", action="store_true", dest="framework", help="attempt to update only ovs-framework")
parser.add_option("-v", "--volumedriver", action="store_true", dest="volumedriver", help="attempt to update only volumedriver")
parser.add_option("-a", "--alba", action="store_true", dest="alba", help="attempt to update only alba backend")
parser.add_option("-s", "--sync", action="store_true", dest="sync", help="sync apt-get archives directory (download faster)")
parser.add_option("-O", "--stop-vm", action="store_true", dest="stopVM", help="stop all running vm")
parser.add_option("-A", "--start-vm", action="store_true", dest="startVM", help="start previously stopped vm")
parser.add_option("-k", "--skip-vm", action="store_true", dest="skip", help="do not start/stop vm during update")
(options, args) = parser.parse_args()

# hosts to skip
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

def executeOnNodes(nodes, command):
    for ns in nodes:
        if ns.instance not in hosts:
            return ns.execute(command)

def getGenericFiles(nodes, path, extstrip):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            command = "(basename -s %s -a $(ls %s)) 2> /dev/null; exit 0" % (extstrip, path)
            content = ns.execute(command)
            
            if content == "":
                return []
            
            return content.split("\r\n")

def getOvsStuffName(nodes, prefix):
    return getGenericFiles(nodes, '/etc/init/ovs-%s*conf' % prefix, '.conf')

def getGenericStuffName(nodes, prefix):
    return getGenericFiles(nodes, '/etc/init/%s*conf' % prefix, '.conf')

"""
start - stop - restart
"""
def restartServiceName(nodes, service):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute("stop %s; exit 0" % service)
            ns.execute("start %s" % service)

def restartServices(nodes, services):
    for service in services:
        restartServiceName(nodes, service)

def startServiceName(nodes, service):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute("start %s" % service)

def startServices(nodes, services):
    for service in services:
        startServiceName(nodes, service)

def stopServiceName(nodes, service):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute("stop %s" % service)

def stopServices(nodes, services):
    for service in services:
        stopServiceName(nodes, service)

"""

"""
def pidFromStatus(singleNode, service):
    return singleNode.execute("status %s | grep 'running' | awk '{ print $4 }'" % service)

def killPid(singleNode, pid):
    singleNode.execute("kill %s" % pid)

def nodesList(sshservices):
    items = []
    
    for ns in sshservices:
        if ns.instance not in hosts:
            items.append(ns)
    
    return items

"""
virtual machine state manager
"""
def runningMachinesOnNode(node):
    buffer = executeOnNodes([node], "virsh -q list | awk '{ print $2 }'")
    
    if buffer == "":
        return []
    
    return buffer.split("\r\n")

def stopMachinesOnNode(node, machines):
    print '[+] stopping VMs on node: %s' % node.instance
        
    for vm in machines:
        executeOnNodes([node], "virsh shutdown %s" % vm)
    
    stillRunning = runningMachinesOnNode(node)
    print '[+] waiting VMs to stop...'
    
    while len(stillRunning) > 0:        
        print '[+] still running VMs: %d, waiting for shutdown' % len(stillRunning)
        
        time.sleep(5)
        stillRunning = runningMachinesOnNode(node)
    
    return True

def startMachinesOnNode(node, machines):
    print '[+] starting VMs on node: %s' % node.instance
        
    for vm in machines:
        executeOnNodes([node], "virsh start %s" % vm)

def waitPathReachable(node, path):
    reachable = False
    
    while not reachable:
        buffer = executeOnNodes([node], "ls '%s'; exit 0" % path)
        
        if "ls: cannot access" in buffer:
            print '[-] %s is not reachable on %s, waiting...' % (path, ns.instance)
            time.sleep(5)
            
        else:
            reachable = True
    
    return True

def saveMachinesState(nodes):
    filename = '/tmp/ovs-machine-state.json'
    running  = {}
    
    # If already exists, load from backup
    if j.system.fs.exists(filename):
        print '[+] saved list found, loading it'
        with open(filename, 'r') as f:
            running = json.load(f)
    
    # Building machine list
    else:
        for node in nodes:
            running[node.instance] = runningMachinesOnNode(node)
    
    print '[+] running VMs are:'
    print running
    
    with open(filename, 'w') as f:
            json.dump(running, f, indent=4)
    
    print '[+] list saved to: %s' % filename
    
    return running

def loadMachinesState(nodes):
    filename = '/tmp/ovs-machine-state.json'
    running  = {}
    
    # If already exists, load from backup
    if j.system.fs.exists(filename):
        print '[+] saved list found, loading it'
        with open(filename, 'r') as f:
            running = json.load(f)
    
    else:
        print '[-] no saved state found'
    
    return running

def update(nodes):    
    for node in nodes:
        executeOnNodes([node], "apt-get update")

def checker(nodes):
    status = {
        'arakoon': False,
        'framework': False,
        'volumedriver': False,
        'alba': False
    }
    
    for node in nodes:
        # note: exit 0 override the return 1 of apt-get which is not an error
        update = executeOnNodes([node], "apt-get -u upgrade --assume-no; exit 0")
        break
        
    if "openvstorage" in update:
        status['framework'] = True
    
    if "volumedriver" in update:
        status['volumedriver'] = True
    
    if "alba" in update:
        status['alba'] = True
    
    if "arakoon" in update:
        status['arakoon'] = True
    
    return status


"""
updaters
"""
def framework(nodes):
    alreadyup = False
    
    for node in nodes:
        # Stopping services
        services = getOvsStuffName([node], "watcher-framework")
        stopServices([node], services)
        
        executeOnNodes([node], "/etc/init.d/memcached stop")
        
        services = getOvsStuffName([node], "arakoon-ovsdb")
        stopServices([node], services)
    
    for node in nodes:
        # Updating openvstorage
        executeOnNodes([node], "touch /etc/ready_for_upgrade")
        executeOnNodes([node], "apt-get install -y --force-yes openvstorag*")
    
    for node in nodes:
        executeOnNodes([node], "/etc/init.d/memcached start")
        
        services = getOvsStuffName([node], "arakoon-ovsdb")
        startServices([node], services)
    
    # Post upgrade
    for node in nodes:
        executeOnNodes([node], "python /opt/code/git/0-complexity/openvcloud/scripts/ovs/post-upgrade-single.py")
        break
    
    executeOnNodes(nodes, "python /opt/code/git/0-complexity/openvcloud/scripts/ovs/post-upgrade-all.py")
    
    for node in nodes:
        executeOnNodes([node], "/etc/init.d/memcached restart")
    
    for node in nodes:
        services = getOvsStuffName([node], "watcher-framework")
        restartServices([node], services)
    
    for node in nodes:
        # apply patch
        executeOnNodes([node], 'sed -i.bak "s/^ALLOWED_HOSTS.*$/ALLOWED_HOSTS = [\'*\']/" /opt/OpenvStorage/webapps/api/settings.py')
        services = getOvsStuffName([node], "webapp-api")
        restartServices([node], services)
    
    for node in nodes:
        executeOnNodes([node], "ays restart -n nginx")
    
    print '[+] framework updated !'



def volumedriver(nodes):
    for node in nodes:
        # Updating volumedriver
        executeOnNodes([node], "apt-get install -y --force-yes volumedriver-base volumedriver-server")
    
    for node in nodes:
        # Restarting services
        services = getOvsStuffName([node], "volumedriver_")
        restartServices([node], services)
    
    print '[+] volumedriver updated !'



def arakoon(nodes):
    for node in nodes:
        # Updating volumedriver
        # executeOnNodes([node], "apt-get install -y --force-yes arakoon")
        print node
    
    # Restart clusters    
    clusters = getGenericFiles([node], "/opt/OpenvStorage/config/arakoon/", "XXX")
    upscript = '/opt/code/git/0-complexity/openvcloud/scripts/ovs/arakoon-restart.py'
    backcmd  = "ip -4 -o addr show dev backplane1 | awk '{ print $4 }' | cut -d'/' -f 1"
    
    # FIXME: better way ?
    for node in nodes:
        break
    
    backplane = executeOnNodes([node], backcmd)
    
    for cluster in clusters:
        # executeOnNodes([node], "python %s --cluster %s --address %s")
        print "python %s --cluster %s --address %s" % (upscript, cluster, backplane)
    
    print '[+] arakoon updated !'



def alba(nodes):
    # Updating alba
    for node in nodes:
        executeOnNodes([node], "apt-get install -y --force-yes alba")
    
    # Restarting each ASD
    for node in nodes:
        services = getGenericStuffName([node], "alba-asd-")
        restartServices([node], services)
    
    # Restarting all proxies
    for node in nodes:
        services = getOvsStuffName([node], "albaproxy_")
        for service in services:
            pid = pidFromStatus(node, service)
            
            print '[+] killing %s on %s' % (pid, node.instance)
            killPid(node, pid)
    
    for node in nodes:
        services = getOvsStuffName([node], "arakoon-")
        for service in services:
            restartServiceName([node], service)
            time.sleep(40)
    
    for node in nodes:
        services = getOvsStuffName([node], "alba-maintenance")
        restartServices([node], services)
    
    for node in nodes:
        services = getOvsStuffName([node], "alba-rebalancer")
        restartServices([node], services)
    
    print '[+] alba updated !'

"""
virtual machines
"""
def stopAll(nodes, running):
    print '[+] stopping virtual machines'
    for node in nodes:
        stopMachinesOnNode(node, running[node.instance])
    
def startAll(nodes, running):
    print '[+] starting virtual machines'
    for node in nodes:
        startMachinesOnNode(node, running[node.instance])

"""
online/offline tools
"""
def preprocess(nodes):
    print '[+] stopping agent to prevent any operation during update'
    for node in nodes:
        executeOnNodes([node], "fuser -k 4446/tcp")
    
def postprocess(nodes):
    print '[+] restarting agent'
    for node in nodes:
        executeOnNodes([node], "ays start -n jsagent")

def vmStatus():
    if j.system.fs.exists('/tmp/ovs-machine-state.json'):
        print '[-] machine state already found, did you forget --skip ?'
        j.application.stop()
    
    return True


"""
worker
"""
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)
nodes = nodesList(sshservices)

if options.check:    
    print '[+] checking updates status (don\'t forget to --update before)'
    status = checker(nodes)
    
    print '[+] update for arakoon: %s' % status['arakoon']
    print '[+] update for framework: %s' % status['framework']
    print '[+] update for volumedriver: %s' % status['volumedriver']
    print '[+] update for alba: %s' % status['alba']

if options.update:
    print '[+] updating repositories on each nodes'
    update(nodes)

if options.arakoon:
    if not options.skip:
        running = saveMachinesState(nodes)
        stopAll(nodes, running)
    
    print '[+] updating arakoon'
    arakoon(nodes)
    
    if not options.skip:
        startAll(nodes, running)

if options.framework:
    print '[+] updating framework'
    framework(nodes)

if options.volumedriver:
    if not options.skip:
        vmStatus() # Check if state already exists       
        running = saveMachinesState(nodes)
        stopAll(nodes, running)
    
    print '[+] updating volumedriver'
    volumedriver(nodes)
    
    if not options.skip:
        startAll(nodes, running)

if options.alba:
    if not options.skip:
        vmStatus() # Check if state already exists
        running = saveMachinesState(nodes)
        stopAll(nodes, running)
    
    print '[+] updating alba'
    alba(nodes)
    
    if not options.skip:
        startAll(nodes, running)
    
if options.stopVM:
    running = saveMachinesState(nodes)
    
    print '[+] stopping virtual machines'
    for node in nodes:
        stopMachinesOnNode(node, running[node.instance])

if options.startVM:
    running = loadMachinesState(nodes)
    
    print '[+] starting virtual machines'
    for node in nodes:
        startMachinesOnNode(node, running[node.instance])

if options.prepro:
    print '[+] pre-processing stuff'
    preprocess(nodes)
    
if options.postpro:
    print '[+] post-processing stuff'
    postprocess(nodes)


j.application.stop()
