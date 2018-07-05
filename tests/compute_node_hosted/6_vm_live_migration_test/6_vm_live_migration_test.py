#!/usr/local/bin/jspython
from JumpScale import j
import uuid
import sys
import os
import time
import ConfigParser
from fabric import network
import multiprocessing

def main():
    config = ConfigParser.ConfigParser()
    config.read("functional_testing/Openvcloud/compute_node_hosted/6_vm_live_migration_test/parameters.cfg")
    cpu = int(config.get("parameters", "cpu"))
    memory = int(config.get("parameters", "memory"))
    Bdisksize = int(config.get("parameters", "Bdisksize"))
    no_of_disks=0; data_disksize=0;
    vm_specs = [no_of_disks, data_disksize, Bdisksize, memory, cpu]

    ccl = j.clients.osis.getNamespace('cloudbroker')
    pcl = j.clients.portal.getByInstance('main')
    scl = j.clients.osis.getNamespace('system')

    j.do.execute('apt-get install sshpass')
    sys.path.append(os.getcwd())
    from performance_testing.utils import utils
    USERNAME = 'vmlivemigrateuser'
    email = "%s@test.com" % str(uuid.uuid4())[0:8]
    utils.create_user(USERNAME, email,  pcl, scl)
    ACCOUNTNAME = str(uuid.uuid4())[0:8]
    accountId = utils.create_account(USERNAME, email, ACCOUNTNAME, ccl, pcl)
    cloudspace = utils.create_cloudspace(accountId, USERNAME, ccl, pcl)
    cloudspace_publicport = 6000

    current_stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
    stacks=utils.get_stacks(ccl)
    stacks.remove(current_stack['id'])
    stackid = stacks[0]

    print('A new machine will be created on the node with stackId:%s' %stackid)
    [machineId, cloudspace_publicip] = utils.create_machine_onStack(stackid, cloudspace, 0, ccl, pcl, scl, vm_specs, cloudspace_publicport, Res_dir='test_res')


    machine = pcl.actors.cloudapi.machines.get(machineId)
    account = machine['accounts'][0]

    try:
        if not j.system.net.waitConnectionTest(cloudspace_publicip, cloudspace_publicport, 40):
            print 'Could not connect to VM over public interface'
        else:
            connection = j.remote.cuisine.connect(cloudspace_publicip, cloudspace_publicport, account['password'], account['login'])
            connection.fabric.state.output["running"]=False
            connection.fabric.state.output["stdout"]=False
            connection.user(account['login'])
            connection.apt_get('update')
            connection.apt_get('install fio')

        j.do.execute('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' -P %s functional_testing/Openvcloud/compute_node_hosted/6_vm_live_migration_test/machine_script.py %s@%s:'
                             %(account['password'], cloudspace_publicport, account['login'], cloudspace_publicip))
        j.do.execute('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' -P %s functional_testing/Openvcloud/compute_node_hosted/6_vm_live_migration_test/check_script.py %s@%s:'
                             %(account['password'], cloudspace_publicport, account['login'], cloudspace_publicip))

        network.disconnect_all()
        processes=[]
        for i in range(2):
            if i==0:
                p = multiprocessing.Process(target=utils.run_script, args=(account, cloudspace_publicip, cloudspace_publicport, 'test1'))
                processes.append(p)
            else:
                p = multiprocessing.Process(target=pcl.actors.cloudbroker.machine.moveToDifferentComputeNode, args=(machineId, 'Testing', stacks[1], False))
                processes.append(p)
        for l in range(len(processes)):
            if l == 0:
                print('started writing a file on the created machine ...')
            processes[l].start()
            if l == 1:
                time.sleep(7)
                machine_db = ccl.vmachine.get(machineId)
                if machine_db.status=='RUNNING' and machine_db.stackId==stacks[1]:
                    print('The VM have been successfully installed on other node with approximately no downtime during live migration')
                else:
                    print('A high downtime (more than 7 secs) have been noticed')
                    return None
            time.sleep(15)
            if l == 0:
                print('Machine will be moved to the node with stackId:%s' %stacks[1])
        for k in range(len(processes)):
            processes[k].join()

        network.disconnect_all()
        print('writing a second file to compare with ...')
        utils.run_script(account, cloudspace_publicip, cloudspace_publicport, 'test2')

        network.disconnect_all()
        print('checking if there is no data loss ...')
        test_result = utils.check_script(account, cloudspace_publicip, cloudspace_publicport, 'test1.1.0', 'test2.1.0')
        if test_result != 'Two files are identical':
            print('There is a data loss')
        j.do.execute('ssh-keygen -f "/root/.ssh/known_hosts" -R [%s]:%s'%(cloudspace_publicip, cloudspace_publicport))
        return test_result
    finally:
        j.do.execute('ssh-keygen -f "/root/.ssh/known_hosts" -R [%s]:%s'%(cloudspace_publicip, cloudspace_publicport))


if __name__ == "__main__":
    try:
        test_result = main()
    finally:
        j.do.execute('jspython performance_testing/scripts/tear_down.py vmlivemigrateuser')
        try:
            if test_result == 'Two files are identical':
                print ('################ \n# Test succeed #\n################')
            else:
                print ('############### \n# Test Failed # \n###############')
        except NameError:
            print ('############### \n# Test Failed # \n###############')
