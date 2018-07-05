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
    config.read("functional_testing/Openvcloud/compute_node_hosted/8_node_maintenance_test/parameters.cfg")
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
    USERNAME = 'nodemaintenanceuser'
    email = "%s@test.com" % str(uuid.uuid4())[0:8]
    utils.create_user(USERNAME, email,  pcl, scl)
    ACCOUNTNAME = str(uuid.uuid4())[0:8]
    accountId = utils.create_account(USERNAME, email, ACCOUNTNAME, ccl, pcl)
    cloudspace = utils.create_cloudspace(accountId, USERNAME, ccl, pcl)
    cloudspace_publicport = 8000

    current_stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
    stacks=utils.get_stacks(ccl)
    stacks.remove(current_stack['id'])
    stackid = stacks[0]

    print('A new machine will be created on the node with stackId:%s' %stackid)
    [machineId, cloudspace_publicip] = utils.create_machine_onStack(stackid, cloudspace, 0, ccl, pcl, scl, vm_specs, cloudspace_publicport, Res_dir='test_res')


    utils.setup_machine(cloudspace, machineId, cloudspace_publicport, pcl, no_of_disks, 'onlyfio')

    machine = pcl.actors.cloudapi.machines.get(machineId)
    account = machine['accounts'][0]
    j.do.execute('sshpass -p%s scp -o \'StrictHostKeyChecking=no\' -P %s functional_testing/Openvcloud/compute_node_hosted/8_node_maintenance_test/machine_script.py %s@%s:'
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
            gid = ccl.stack.get(ccl.vmachine.get(machineId).stackId).gid
            p = multiprocessing.Process(target=pcl.actors.cloudbroker.computenode.maintenance, args=(stackid, gid,'move', 'testing'))
            processes.append(p)
    for l in range(len(processes)):
        if l == 0:
            print('started writing a file on the created machine ...')
        processes[l].start()
        if l == 1:
            time.sleep(10)
            machine_db = ccl.vmachine.get(machineId)
            if machine_db.stackId==stackid:
                print('VM didn\'t move to another stackId')
                return [None, stackid, gid]
            else:
                if machine_db.status=='RUNNING':
                    print('The VM have been successfully installed on other node with approximately no downtime during cpu node maintenance')
                else:
                    print('A high downtime have been noticed')
                    return [None, stackid, gid]
        time.sleep(12)
        if l == 0:
            print('cpu node with stackid:%s will be put in maintenance ..'% stackid)
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
    return [test_result, stackid, gid]


if __name__ == "__main__":
    try:
        [test_result, stackid, gid] = main()
    finally:
        j.do.execute('jspython performance_testing/scripts/tear_down.py nodemaintenanceuser')
        try:
            pcl = j.clients.portal.getByInstance('main')
            pcl.actors.cloudbroker.computenode.enable(id=stackid, gid=gid, message='testing')
            if test_result == 'Two files are identical':
                print ('################ \n# Test succeed #\n################')
            else:
                print ('############### \n# Test Failed # \n###############')
        except NameError:
            print ('############### \n# Test Failed # \n###############')
