#!/usr/local/bin/jspython
from JumpScale import j
import uuid
import sys
import os
from fabric import network
import netaddr
import re

ccl = j.clients.osis.getNamespace('cloudbroker')
pcl = j.clients.portal.getByInstance('main')
scl = j.clients.osis.getNamespace('system')

j.do.execute('apt-get install sshpass')
sys.path.append(os.getcwd())
from performance_testing.utils import utils
USERNAME = 'networktestuser'
email = "%s@test.com" % str(uuid.uuid4())[0:8]
utils.create_user(USERNAME, email,  pcl, scl)
ACCOUNTNAME = str(uuid.uuid4())[0:8]
accountId = utils.create_account(USERNAME, email, ACCOUNTNAME, ccl, pcl)
cloudspace = utils.create_cloudspace(accountId, USERNAME, ccl, pcl)
cloudspace_publicport = 1000

cloudspace_publicIP = str(netaddr.IPNetwork(cloudspace['publicipaddress']).ip)

if not j.system.net.waitConnectionTest(cloudspace_publicIP, 9080, 60):
    print 'Could not connect to VM over public interface'

current_stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
stacks=utils.get_stacks(ccl)
cpu=2; memory=2048; Bdisksize=100; no_of_disks=0; data_disksize=0;
vm_specs = [no_of_disks, data_disksize, Bdisksize, memory, cpu]

machines=[]
for stackid in stacks:
    if stackid == current_stack['id']:
        continue
    print('creating machine on stack: %s and checking if it is accessible on public interface' %stackid)
    machineId = utils.create_machine_onStack(stackid, cloudspace, 0, ccl, pcl, scl, vm_specs, cloudspace_publicport, Res_dir=None)
    machines.append([machineId, cloudspace_publicport])
    cloudspace_publicport += 1

j.do.execute('echo \'This line is for test\' >> noerror.txt')

for vm in machines:
    vmId = vm[0]
    cloudspace_publicport = vm[1]
    machine = pcl.actors.cloudapi.machines.get(vmId)
    account = machine['accounts'][0]
    j.do.execute('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' -P %s noerror.txt  %s@%s:'
                 %(account['password'], cloudspace_publicport, account['login'], cloudspace_publicIP))
    j.do.execute('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' -P %s functional_testing/Openvcloud/compute_node_hosted/1_Network_config_test/machine_script.py  %s@%s:'
                 %(account['password'], cloudspace_publicport, account['login'], cloudspace_publicIP))
    connection = j.remote.cuisine.connect(cloudspace_publicIP, cloudspace_publicport, account['password'], account['login'])
    connection.user(account['login'])
    connection.fabric.state.output["running"]=False
    connection.fabric.state.output["stdout"]=False
    connection.apt_get('install sshpass')
    connection.run('python machine_script.py noerror.txt')


network.disconnect_all()
for vm in machines:
    vmId = vm[0]
    cloudspace_publicport = vm[1]
    machine = pcl.actors.cloudapi.machines.get(vmId)
    account = machine['accounts'][0]
    connection = j.remote.cuisine.connect(cloudspace_publicIP, cloudspace_publicport, account['password'], account['login'])
    connection.fabric.state.output["running"]=False
    connection.fabric.state.output["stdout"]=False
    connection.user(account['login'])
    connection.run('echo \'This line is for test\' >> noerror%s.txt' %vmId)
    for vmach in machines:
        vmachId = vmach[0]
        if vmachId==vmId:
            continue
        machine = pcl.actors.cloudapi.machines.get(vmachId)
        account = machine['accounts'][0]
        machine_ip = machine['interfaces'][0]['ipAddress']
        connection.run('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' noerror%s.txt  %s@%s:'
                 %(account['password'], vmId, account['login'], machine_ip))
        connection1 = j.remote.cuisine.connect(cloudspace_publicIP, cloudspace_publicport, account['password'], account['login'])
        connection1.fabric.state.output["running"]=False
        connection1.fabric.state.output["stdout"]=False
        connection1.user(account['login'])
        connection1.run('python machine_script.py noerror%s.txt' %vmId)
j.do.execute('rm noerror.txt')

for vm in machines:
    vmId = vm[0]
    cloudspace_publicport = vm[1]
    machine = pcl.actors.cloudapi.machines.get(vmId)
    account = machine['accounts'][0]
    f = open("final.txt", 'a')
    j.do.execute('sshpass -p%s scp -r -o \'StrictHostKeyChecking=no\' -P %s  %s@%s:results.txt .'
                 %(account['password'], cloudspace_publicport, account['login'], cloudspace_publicIP))
    res = open("results.txt", 'r')
    f.write(res.read())
    f.close()
    j.do.execute('rm results.txt')

f = open("final.txt", 'r')
match = re.search('Verification failed', f.read())
if match:
     print ('############### \n# Test Failed # \n###############')
else:
    print ('################ \n# Test succeed #\n################')

#Removing vms fingerprints from known hosts
for vm in machines:
    cloudspace_publicport = vm[1]
    j.do.execute('ssh-keygen -f "/root/.ssh/known_hosts" -R [%s]:%s'%(cloudspace_publicIP, cloudspace_publicport))
j.do.execute('rm final.txt')
j.do.execute('jspython performance_testing/scripts/tear_down.py networktestuser')

















