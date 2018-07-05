#!/usr/local/bin/jspython
from JumpScale import j
import uuid
import sys
import os
import ConfigParser
import datetime


def main():
    config = ConfigParser.ConfigParser()
    config.read("functional_testing/Openvcloud/compute_node_hosted/3_Env_Limit_test/parameters.cfg")
    cpu = int(config.get("parameters", "cpu"))
    memory = int(config.get("parameters", "memory"))
    Bdisksize = int(config.get("parameters", "Bdisksize"))
    needed_vms = int(config.get("parameters", "vms"))
    no_of_disks=0; data_disksize=0;
    vm_specs = [no_of_disks, data_disksize, Bdisksize, memory, cpu]
    Res_dir = config.get("parameters", "Res_dir")

    j.do.execute("mkdir -p %s" %Res_dir)
    hostname = j.do.execute('hostname')[1].replace("\n","")
    test_num = len(os.listdir('%s'%Res_dir))+1
    test_folder = "/"+datetime.datetime.today().strftime('%Y-%m-%d')+"_"+hostname+"_testresults_%s"%test_num
    Res_dir = Res_dir + test_folder

    try:
        if not j.do.exists('%s' % Res_dir):
            j.do.execute('mkdir -p %s' % Res_dir)

        ccl = j.clients.osis.getNamespace('cloudbroker')
        pcl = j.clients.portal.getByInstance('main')
        scl = j.clients.osis.getNamespace('system')

        USERNAME = 'envlimittestuser'
        email = "%s@test.com" % str(uuid.uuid4())[0:8]
        utils.create_user(USERNAME, email,  pcl, scl)
        ACCOUNTNAME = str(uuid.uuid4())[0:8]
        accountId = utils.create_account(USERNAME, email, ACCOUNTNAME, ccl, pcl)

        current_stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
        stacks=utils.get_stacks(ccl)

        cloudspace_publicport = 3000
        cloudspaces=[]
        for stackid in stacks:
            if stackid == current_stack['id']:
                continue
            print('creating cloudspace and corresponding vm ')
            loc = ccl.location.search({})[1]['locationCode']
            # change this to cloudbroker later, after api is fixed
            cloudspaceId = pcl.actors.cloudapi.cloudspaces.create(accountId=accountId,location=loc,name='CS%s'%stackid,access=USERNAME)
            pcl.actors.cloudbroker.cloudspace.deployVFW(cloudspaceId)
            cloudspace = ccl.cloudspace.get(cloudspaceId).dump()
            utils.create_machine_onStack(stackid, cloudspace, 0, ccl, pcl, scl, vm_specs, cloudspace_publicport, Res_dir='wait_for_VMIP')
            cloudspaces.append([cloudspace, stackid])
            cloudspace_publicport += 1
        vms = 3
        iteration=1
        while(True):
            for cloudspace in cloudspaces:
                cs = cloudspace[0]
                stackid = cloudspace[1]
                try:
                    print('creating VM No:%s' %(vms+1))
                    utils.create_machine_onStack(stackid, cs, iteration, ccl, pcl, scl, vm_specs, cloudspace_publicport, Res_dir='wait_for_VMIP')
                    vms += 1
                    if needed_vms == vms+1 and needed_vms != 0:
                        return [[[cpu, memory, Bdisksize, needed_vms]], Res_dir]
                except:
                    print('   |--failed to create the machine')
                    return [[[cpu, memory, Bdisksize, vms]], Res_dir]

            iteration += 1
    except:
        print('Found problems during running the test.. removing results directory..')
        j.do.execute('rm -rf %s' %results[1])
        raise


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from performance_testing.utils import utils
    try:
        results = main()
        titles = ['VM_CPU\'s', 'VM_Memory(MB)', 'HDD(GB)', 'Total VMs created']
        utils.collect_results(titles, results[0], '%s' %results[1])
        utils.push_results_to_repo(results[1])
    finally:
        j.do.execute('jspython performance_testing/scripts/tear_down.py envlimittestuser')



