from JumpScale import j
from optparse import OptionParser

# hosts to skip
hosts = ['ovc_master', 'ovc_proxy', 'ovc_reflector', 'ovc_dcpm']

def executeOnNode(nodes, command):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            return ns.execute(command)

def executeOnNodes(nodes, command):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute(command)

def getOvsStuffName(nodes, prefix):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            command = "basename -s .conf -a $(ls /etc/init/ovs-%s*conf)" % prefix
            content = ns.execute(command)
            return content.split("\r\n")

def restartServiceName(nodes, service):
    for ns in nodes:
        if ns.instance not in hosts:
            print '[+] executing on: %s' % ns.instance
            ns.execute("restart %s" % service)

def restartServices(nodes, services):
    for service in services:
        restartServiceName(nodes, service)

def pidFromStatus(singleNode, service):
    return singleNode.execute("status %s | grep 'running' | awk '{ print $4 }'" % service)

def killPid(singleNode, pid):
    singleNode.execute("kill %d" % pid)

sshservices = j.atyourservice.findServices(name='node.ssh')
sshservices.sort(key = lambda x: x.instance)

""" Update stuff """
print '[+] updating repositories on each nodes'
executeOnNodes(sshservices, "apt-get update")

print '[+] checking what need to be updated'
# node: exit 0 override the return 1 of apt-get which is not an error
update = executeOnNode(sshservices, "apt-get -u upgrade --assume-no; exit 0")
alreadyup = True

""" Volume Driver """
if "volumedriver" in update:
    alreadyup = False
    """ Stuff """
    
    # Stop all virtual machines
    # ...
    
    # Updating volumedriver
    executeOnNodes(sshservices, "apt-get install -y --force-yes volumedriver-base volumedriver-server")
    
    # Restarting services
    services = getOvsStuffName(sshservices, "volumedriver_")
    restartServices(services)
    
else:
    print '[+] volumedriver is up-to-date'


""" Alba """
if "alba" in update:
    alreadyup = False
    """ Stuff """
    
    # Stop volumes
    # ...
    
    # Updating volumedriver
    # executeOnNodes(sshservices, "apt-get install -y --force-yes alba")
    
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
    
else:
    print '[+] alba is up-to-date'


""" We are done """
if alreadyup:
    print '[+] everything is up-to-date'

else:
    print '[+] update finished'


