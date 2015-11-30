from JumpScale import j
from optparse import OptionParser
import time

# hosts to skip
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

def executeOnNode(nodes, command):
    for ns in nodes:
        if ns.instance not in hosts:
            return ns.execute(command)

def executeOnNodes(nodes, command):
    for ns in nodes:
        if ns.instance not in hosts:
            ns.execute(command)

def getOvsStuffName(nodes, prefix):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            command = "basename -s .conf -a $(ls /etc/init/ovs-%s*conf)" % prefix
            content = ns.execute(command)
            return content.split("\r\n")

"""
start - stop - restart
"""
def restartServiceName(nodes, service):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute("restart %s" % service)

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
    singleNode.execute("kill %d" % pid)

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
    buffer = executeOnNode([node], "virsh -q list | awk '{ print $2 }'")
    
    if buffer == "":
        return []
    
    return buffer.split("\r\n")

def stopMachinesOnNode(node, machines):
    print '[+] stopping VMs on node: %s' % node.instance
        
    for vm in machines:
        executeOnNode([node], "virsh shutdown %s" % vm)
    
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
        executeOnNode([node], "virsh start %s" % vm)

def waitPathReachable(node, path):
    reachable = False
    
    while not reachable:
        buffer = executeOnNode([node], "ls '%s'; exit 0" % path)
        
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
    
    return running

"""
worker
"""
sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)

""" Update stuff """
print '[+] updating repositories on each nodes'
executeOnNodes(sshservices, "apt-get update")

print '[+] checking what need to be updated'
# node: exit 0 override the return 1 of apt-get which is not an error
update = executeOnNode(sshservices, "apt-get -u upgrade --assume-no; exit 0")
alreadyup = True

nodes = nodesList(sshservices)

"""
FIXME: only stop one time all vm if multiple update occure
FIXME: add arguments to do some specific part
FIXME: save running vm to a file to keep it alive even if script fail
"""
if "openvstorage" in update or True:
    alreadyup = False
    """ Stuff """
    
    running = saveMachinesState(nodes)
    
    for node in nodes:
        running[node.instance] = runningMachinesOnNode(node)
    
    print '[+] running VMs are:'
    print running
    
    for node in nodes:
        # Stopping all virtual machines
        stopMachinesOnNode(node, running[node.instance])
        print '[+] machines stopped'
    
    for node in nodes:
        # Updating openvstorage
        executeOnNode([node], "touch /etc/ready_for_upgrade")
        executeOnNode([node], "apt-get install -y --force-yes openvstorag*")
    
    index = 1
    for node in nodes:
        # Restarting services
        services = getOvsStuffName([node], "watcher-framework")
        restartServices([node], services)
        
        services = getOvsStuffName([node], "worker")
        restartServices([node], services)
        
        if index < 4:
            services = getOvsStuffName([node], "webapp-api")
            restartServices([node], services)
            index += 1
    
    # Post upgrade
    for node in nodes:
        executeOnNode([node], "python /opt/code/git/0-complexity/openvcloud/scripts/updates/ovs-post-upgrade-single.py")
        break
    
    executeOnNodes(sshservices, "python /opt/code/git/0-complexity/openvcloud/scripts/updates/ovs-post-upgrade-all.py")
    # executeOnNodes(sshservices, 'python /opt/code/git/0-complexity/openvcloud/scripts/updates/ovs-post-upgrade.py')
    
    # Checking if volume is reachable
    for node in nodes:
        print '[+] checking vmstor on node %s' % node.instance
        waitPathReachable(node, '/mnt/vmstor/templates')
    
    # running = {'du-conv-1-03': ['vm-117', 'routeros_00d0', 'vm-106', 'vm-112', 'vm-50', 'routeros_00d6', 'vm-120', 'vm-121', 'vm-123', 'vm-209', 'vm-216', 'routeros_00d3'], 'du-conv-1-02': ['routeros_00cb', 'vm-110', 'vm-81', 'vm-122', 'vm-197', 'vm-205', 'vm-214'], 'du-conv-1-01': ['routeros_00c9', 'vm-108', 'vm-109', 'vm-43', 'vm-54', 'routeros_00d5', 'vm-181', 'vm-182', 'vm-190', 'vm-199', 'routeros_00cc', 'vm-223'], 'du-conv-1-04': ['routeros_00d7', 'routeros_00ca', 'routeros_00cf', 'vm-111', 'vm-44', 'vm-47', 'vm-48', 'vm-51', 'vm-57', 'vm-62', 'vm-210', 'vm-211', 'vm-212', 'routeros_00dc', 'vm-219']}

    # Restarting VMm when everything is up-to-date
    for node in nodes:
        print '[+] starting machines on node %s' % node.instance
        startMachinesOnNode(node, running[node.instance])
    
    print '[+] openvstorage updated !'
    # j.application.stop()

""" Volume Driver """
if "volumedriver" in update:
    alreadyup = False
    """ Stuff """
    
    # Grabbing running vm
    running = {}
    
    for node in nodes:
        running[node.instance] = runningMachinesOnNode(node)
    
    print '[+] running VMs are:'
    print running
    
    for node in nodes:
        # Stopping all virtual machines
        stopMachinesOnNode(node, running[node.instance])
        print '[+] machines stopped'
    
    for node in nodes:
        # Updating volumedriver
        executeOnNode([node], "apt-get install -y --force-yes volumedriver-base volumedriver-server")
    
    for node in nodes:
        # Restarting services
        services = getOvsStuffName([node], "volumedriver_")        
        restartServices([node], services)
    
    # Checking if volume is reachable
    for node in nodes:
        print '[+] checking vmstor on node %s' % node.instance
        waitPathReachable(node, '/mnt/vmstor/templates')
    
    # running = {'du-conv-1-03': ['vm-117', 'routeros_00d0', 'vm-106', 'vm-112', 'vm-50', 'routeros_00d6', 'vm-120', 'vm-121', 'vm-123', 'vm-209', 'vm-216', 'routeros_00d3'], 'du-conv-1-02': ['routeros_00cb', 'vm-110', 'vm-81', 'vm-122', 'vm-197', 'vm-205', 'vm-214'], 'du-conv-1-01': ['routeros_00c9', 'vm-108', 'vm-109', 'vm-43', 'vm-54', 'routeros_00d5', 'vm-181', 'vm-182', 'vm-190', 'vm-199', 'routeros_00cc', 'vm-223'], 'du-conv-1-04': ['routeros_00d7', 'routeros_00ca', 'routeros_00cf', 'vm-111', 'vm-44', 'vm-47', 'vm-48', 'vm-51', 'vm-57', 'vm-62', 'vm-210', 'vm-211', 'vm-212', 'routeros_00dc', 'vm-219']}

    # Restarting VMm when everything is up-to-date
    for node in nodes:
        print '[+] starting machines on node %s' % node.instance
        startMachinesOnNode(node, running[node.instance])
    
    print '[+] volumedriver updated !'
    # j.application.stop()
    
else:
    print '[+] volumedriver is up-to-date'


""" Alba """
if "alba" in update:
    alreadyup = False
    """ Stuff """
    
    # Stop volumes
    # ...
    
    # Updating alba
    executeOnNodes(sshservices, "apt-get install -y --force-yes alba")
    
    # Restarting each ASD
    services = getOvsStuffName(sshservices, "asd-")
    restartServices(services)
    
    # Restarting all proxies
    services = getOvsStuffName(sshservices, "albaproxy_")
    for service in services:
        for ns in nodes:
            if ns.instance not in hosts:
                pid = pidFromStatus(ns, service)
                
                print '[+] killing %d on %s' % (pid, ns.instance)
                killPid(ns, pid)
    
    services = getOvsStuffName(sshservices, "arakoon-")
    for ns in nodes:
            if ns.instance not in hosts:
                for service in services:
                    restartServiceName([ns], service)
                    time.sleep(40)
    
    services = getOvsStuffName(sshservices, "alba-maintenance")
    restartServices(services)
    
    services = getOvsStuffName(sshservices, "alba-rebalancer")
    restartServices(services)
    
    # Post upgrade
    executeOnNode(sshservices, 'python -c "import sys; sys.path.append(\'/opt/OpenvStorage\'); from ovs.dal.helpers import Migration; Migration.migrate()"')
    executeOnNodes(sshservices, 'python /opt/code/git/0-complexity/openvcloud/scripts/updates/ovs-post-upgrade.py')
    
    print '[+] alba updated !'
    # j.application.stop()
    
else:
    print '[+] alba is up-to-date'


""" We are done """
if alreadyup:
    print '[+] everything is up-to-date'

else:
    print '[+] update finished'


