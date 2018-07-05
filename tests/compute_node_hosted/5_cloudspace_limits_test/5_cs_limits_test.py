#!/usr/local/bin/jspython
from JumpScale import j
import uuid
import sys
import os
import datetime

def main():
    cpus = 1; memory =  1024; Bdisksize = 10; no_of_disks=0; data_disksize=0;
    vm_specs = [no_of_disks, data_disksize, Bdisksize, memory, cpus]

    sys.path.append(os.getcwd())
    from performance_testing.utils import utils

    ccl = j.clients.osis.getNamespace('cloudbroker')
    pcl = j.clients.portal.getByInstance('main')
    scl = j.clients.osis.getNamespace('system')

    USERNAME = 'cslimitsuser'
    email = "%s@test.com" % str(uuid.uuid4())[0:8]
    utils.create_user(USERNAME, email,  pcl, scl)
    ACCOUNTNAME = str(uuid.uuid4())[0:8]
    accountId = utils.create_account(USERNAME, email, ACCOUNTNAME, ccl, pcl)

    current_stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
    stacks=utils.get_stacks(ccl)

    loc = ccl.location.search({})[1]['locationCode']
    cs_No=1
    while(True):
        for stackid in stacks:
            if stackid == current_stack['id']:
                continue
            print('Creating cloudspace No.%s ...'%cs_No)
            cloudspaceId = pcl.actors.cloudapi.cloudspaces.create(accountId=accountId,location=loc,name='CS%s'%cs_No,access=USERNAME)
            print('   |--Deploying cloudspace...')
            try:
                pcl.actors.cloudbroker.cloudspace.deployVFW(cloudspaceId)
                cloudspace = ccl.cloudspace.get(cloudspaceId).dump()
            except:
                print('   |-- No more cloudspaces can be created')
                return [[cpus, memory, Bdisksize, cs_No]]
            try:
                utils.create_machine_onStack(stackid, cloudspace, 0, ccl, pcl, scl, vm_specs, cs_publicport=0, Res_dir='wait_for_VMIP')
                cs_No += 1
            except:
                print('   |--failed to create the machine')
                return [[cpus, memory, Bdisksize, cs_No]]


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from performance_testing.utils import utils

    Res_dir = 'tests_results/CS_limits_results'
    j.do.execute("mkdir -p %s" % Res_dir)
    hostname = j.do.execute('hostname')[1].replace("\n", "")
    test_num = len(os.listdir('%s' % Res_dir)) + 1
    test_folder = "/" + datetime.datetime.today().strftime('%Y-%m-%d') + "_" + hostname + "_testresults_%s" % test_num
    Res_dir = Res_dir + test_folder
    j.do.execute("mkdir -p %s" % Res_dir)

    try:
        results = main()
        titles = ['VM_CPU\'s', 'VM_Memory(MB)', 'HDD(GB)', 'Total cloudspaces created']
        utils.collect_results(titles, results, Res_dir)
    finally:
        j.do.execute('jspython performance_testing/scripts/tear_down.py cslimitsuser')
