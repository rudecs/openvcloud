from JumpScale import j
import uuid
from random import randint
import time


def try_account_read(self, operation='get'):
    if operation == 'get':
        self.lg('- get account with user1')
        user_account = self.user_api.cloudapi.accounts.get(accountId=self.account_id)
        self.assertEqual(user_account['id'], self.account_id)
    elif operation == 'list':
        self.lg('- list accounts with user1')
        user_accounts = self.user_api.cloudapi.accounts.list()
        if len(user_accounts) != 1:
            self.user_api.cloudapi.accounts.get(accountId=self.account_id)
        self.assertEqual(user_accounts[0]['id'], self.account_id)
    elif operation == 'getCreditBalance':
        self.lg('- getCreditBalance account with user1')
        user_account = self.user_api.cloudapi.accounts.getConsumedCloudUnits(accountId=self.account_id)
        self.assertEqual(user_account['CU_M'], 0.0)
    elif operation == 'getCreditHistory':
        self.lg('- getCreditHistory account with user1')
        user_account = self.user_api.cloudapi.accounts.getConsumedCloudUnits(accountId=self.account_id)
        options = ['CU_A', 'CU_C', 'CU_D', 'CU_I', 'CU_NO', 'CU_NP', 'CU_S']
        for opt in options:
            if opt == 'CU_I':
                self.assertEqual(user_account[opt], 1)
                #this line is skipped with https://github.com/0-complexity/openvcloud/issues/1154
                #self.assertEqual(self.user_api.cloudapi.accounts.getConsumedCloudUnitsByType(accountId=self.account_id, cutype=opt), 1)
            else:
                self.assertEqual(user_account[opt], 0)
                #this line is skipped with https://github.com/0-complexity/openvcloud/issues/1154
                #self.assertEqual(self.user_api.cloudapi.accounts.getConsumedCloudUnitsByType(accountId=self.account_id, cutype=opt), 0)
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_account_write(self, operation='create_cloudspace'):
    if operation == 'create_cloudspace':
        self.lg('- create cloudspace on user2 with user1')
        newcloudspaceId = self.cloudapi_cloudspace_create(account_id=self.account_id,
                                                          location=self.location,
                                                          access=self.user,
                                                          api=self.user_api)
        self._cloudspaces = [newcloudspaceId]
    elif operation == 'create_machineTemplate':
        newcloudspaceId = self.account_owner_api.cloudapi.cloudspaces.create(accountId=self.account_id,
                          location=self.location, name=str(uuid.uuid4()).replace('-', '')[0:10],
                          access=self.account_owner, maxMemoryCapacity=1, maxDiskCapacity=1)
        self._cloudspaces = [newcloudspaceId]
        self.assertTrue(newcloudspaceId)
        selected_image = self.account_owner_api.cloudapi.images.list(cloudspaceId=newcloudspaceId)[0]
        machineId = self.cloudapi_create_machine(cloudspace_id=newcloudspaceId,
                                                 api=self.account_owner_api,
                                                 image_id=selected_image['id'])
        self._machines = [machineId]

        self.lg('- stop machine2')
        stopped = self.user_api.cloudapi.machines.stop(machineId=machineId)
        self.assertTrue(stopped, 'machine2 %s did not stopped' % machineId)

        self.lg('- use convert machine2 to template with user1')
        converted = self.user_api.cloudapi.machines.convertToTemplate(machineId=machineId,
                  templatename=str(uuid.uuid4()).replace('-', '')[0:10])
        self.assertTrue(converted, 'Create Template API returned False')
        templates = len(self.account_owner_api.cloudapi.accounts.listTemplates(accountId=self.account_id))
        self.assertEqual(templates, 1, 'We should have only one template for this account not [%s]' % templates)
        counter = 120
        while(counter>0):
            status = self.account_owner_api.cloudapi.accounts.listTemplates(accountId=self.account_id)[0]['status']
            if status == 'CREATED':
                break
            counter-=1
            time.sleep(1)
        self.assertEqual(status, 'CREATED', 'machine did not converted to template')
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_account_admin(self, operation='add_user'):
    if operation == 'add_user':
        self.lg('- create account for user3')
        self.user3 = self.cloudbroker_user_create()
        self.lg('- add user1 to the account created by user2 with read access')
        self.user_api.cloudapi.accounts.addUser(accountId=self.account_id,
                                                userId=self.user3,
                                                accesstype='R')
    elif operation == 'update':
        self.user_api.cloudapi.accounts.update(accountId=self.account_id,
                                               name=self.user)
    elif operation == 'delete_user':
        self.lg('- delete account2: %s with user1' % self.account_id)
        self.user_api.cloudapi.accounts.deleteUser(accountId=self.account_id)
        self.CLEANUP['accountId'].remove(self.account_id)
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_cloudspace_read(self, operation='getCloudspace'):
    if operation == 'getCloudspace':
        self.lg('- get cloudspace with user1')
        cloudspace = self.user_api.cloudapi.cloudspaces.get(cloudspaceId=self.cloudspace_id)
        self.assertEqual(cloudspace['id'],
                         self.cloudspace_id,
                         'user [%s] should have access to get cloudspace [%s] owned by user '
                         '[%s]' % (self.user, self.cloudspace_id, self.account_owner))
    elif operation == 'listCloudspaces':
        self.lg('- list cloudspaces with user1')
        cloudspaces = self.user_api.cloudapi.cloudspaces.list()
        self.assertEqual(len(cloudspaces),
                         1,
                         'user [%s] should have access to list cloudspaces [%s] owned by user '
                         '[%s]' % (self.user, self.cloudspace_id, self.account_owner))
        self.user_api.cloudapi.cloudspaces.get(cloudspaceId=self.cloudspace_id)
    elif operation == 'listMachines':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- List account owner machines')
        owner_vms = self.account_owner_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
        user_vms = self.user_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
        if len(owner_vms) != len(user_vms):
            [self.user_api.cloudapi.machines.get(machineId=vm['id']) for vm in owner_vms]

    elif operation == 'listPortforwarding':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- Create one portforwarding')
        self.add_portforwarding(machine_id=machine_id)
        self.lg('- List portforwarding with new user [user], should return 1 portforwarding')
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.assertEqual(len(portforwarding),
                         1,
                         'user [%s] should have access to list all machine portforwarding in '
                         'cloudspace [%s] owned by user [%s]' % (self.user,
                                                                 self.cloudspace_id,
                                                                 self.account_owner))
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_cloudspace_write(self, operation='cloudspaceDeploy'):
    if operation == 'cloudspaceDeploy':
        self.lg('- deploy cloudspace with new user [user], should succeed')
        self.user_api.cloudapi.cloudspaces.deploy(cloudspaceId=self.cloudspace_id)
        self.wait_for_status('DEPLOYED', self.account_owner_api.cloudapi.cloudspaces.get,
                             cloudspaceId=self.cloudspace_id)
    elif operation == 'cloudspaceDefenseshield':
        self.lg('- deploy cloudspace with new user [user], should succeed')
        self.account_owner_api.cloudapi.cloudspaces.deploy(cloudspaceId=self.cloudspace_id)
        self.wait_for_status('DEPLOYED', self.account_owner_api.cloudapi.cloudspaces.get,
                             cloudspaceId=self.cloudspace_id)
        self.lg('- get Defense Shield of cloudspace with new user [new_user], should succeed')
        defense_shield = self.user_api.cloudapi.cloudspaces.getDefenseShield(cloudspaceId=self.cloudspace_id)
        [self.assertIn(key, defense_shield.keys()) for key in ['url', 'user', 'password']]
        self.assertEqual(defense_shield['user'], 'admin')
    elif operation == 'cloudspacePortforwardingAdd':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- Create one portforwarding')
        self.add_portforwarding(machine_id=machine_id, api=self.user_api)
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.assertEqual(len(portforwarding), 1,
                         "Failed to get the port forwarding for machine[%s]" % machine_id)
    elif operation == 'cloudspacePortforwardingUpdate':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- Create one portforwarding')
        self.add_portforwarding(machine_id=machine_id)
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.lg('- Update portforwarding with new ports')
        portforwarding_id = portforwarding[0]['id']
        cs_publicip = portforwarding[0]['publicIp']
        new_cs_publicport = 445
        new_vm_port = 80
        self.user_api.cloudapi.portforwarding.update(cloudspaceId=self.cloudspace_id,
                                                     id=portforwarding_id,
                                                     publicIp=cs_publicip,
                                                     publicPort=new_cs_publicport,
                                                     machineId=machine_id,
                                                     localPort=new_vm_port,
                                                     protocol='tcp')
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.assertEqual(len(portforwarding), 1,
                         "Failed to get the port forwarding for machine[%s]" % machine_id)
        self.assertEqual(int(portforwarding[0]['publicPort']), new_cs_publicport)
        self.assertEqual(int(portforwarding[0]['localPort']), new_vm_port)
    elif operation == 'cloudspacePortforwardingDelete':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- Create one portforwarding')
        self.add_portforwarding(machine_id=machine_id)
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.lg('- Delete portforwarding')
        portforwarding_id = portforwarding[0]['id']
        self.user_api.cloudapi.portforwarding.delete(cloudspaceId=self.cloudspace_id,
                                                     id=portforwarding_id)
        portforwarding = self.user_api.cloudapi.portforwarding.list(cloudspaceId=self.cloudspace_id,
                                                                    machineId=machine_id)
        self.assertEqual(len(portforwarding), 0,
                         "No port forwarding should be listed on this cloud space anymore")
    elif operation == 'cloudspaceMachineCreate':
        self.lg('- create machine with new user [user], should succeed')
        machine_id = self.cloudapi_create_machine(cloudspace_id=self.cloudspace_id,
                                                  api=self.user_api)
        machines = self.user_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
        self.assertEqual(len(machines), 1, 'Failed to list all account owner machines!')
    elif operation == 'cloudspaceMachineClone':
        self.lg('- create 1 machine for account owner')
        owner_machine_id = self.cloudapi_create_machine(cloudspace_id=self.cloudspace_id,
                                                        api=self.account_owner_api)
        self.lg('- clone created machine with new user [user], should succeed')
        self.api.cloudapi.machines.stop(machineId=owner_machine_id)
        self.wait_for_status('HALTED',
                             self.api.cloudapi.machines.get,
                             machineId=owner_machine_id)
        owner_machine = self.api.cloudapi.machines.get(machineId=owner_machine_id)
        self.assertEqual(owner_machine['status'], 'HALTED')
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        cloned_machine_id = self.user_api.cloudapi.machines.clone(machineId=owner_machine_id,
                                                                  name=name)
        self.wait_for_status('RUNNING',
                             self.api.cloudapi.machines.get,
                             machineId=cloned_machine_id)
        cloned_machine = self.api.cloudapi.machines.get(machineId=cloned_machine_id)
        self.assertEqual(cloned_machine['status'], 'RUNNING')
    elif operation == 'cloudspaceMachineDelete':
        self.lg('- create 1 machine for account owner')
        owner_machine_id = self.cloudapi_create_machine(cloudspace_id=self.cloudspace_id,
                                                        api=self.account_owner_api)
        self.lg('- stop created machine.')
        self.api.cloudapi.machines.stop(machineId=owner_machine_id)
        self.wait_for_status('HALTED',
                             self.api.cloudapi.machines.get,
                             machineId=owner_machine_id)
        owner_machine = self.api.cloudapi.machines.get(machineId=owner_machine_id)
        self.assertEqual(owner_machine['status'], 'HALTED')
        self.lg('- delete created machine with new user [user], should succeed')
        self.user_api.cloudapi.machines.delete(machineId=owner_machine_id)
        machines = self.user_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
        self.assertEqual(len(machines), 0, 'Failed to list all account owner machines!')
    elif operation == 'cloudspaceMachineResize':
        self.lg('- Create 1 machine for account owner')
        machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                  self.account_owner_api)
        self.lg('- New user stop the machine')
        self.user_api.cloudapi.machines.stop(machineId=machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=machine_id)['status'],
                             'HALTED')

        self.lg('4- Resize the machine with new user [user], should succeed')
        sizesAva = len(self.api.cloudapi.sizes.list(self.cloudspace_id))
        resizeId = randint(1, sizesAva)
        self.lg('-resize the machine with sizeId %s'%resizeId)
        self.account_owner_api.cloudapi.machines.resize(machineId=machine_id,
                                               sizeId=resizeId)

        self.lg('5- New user start the machine')
        self.user_api.cloudapi.machines.start(machineId=machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=machine_id)['status'],
                             'RUNNING')

        self.assertEqual(self.api.cloudapi.machines.get(machineId=machine_id)['sizeid'],
                         resizeId)

    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_cloudspace_admin(self, operation='cloudspaceAdduser'):
    if operation == 'cloudspaceAdduser':
        self.lg('- create account for user3')
        user3 = self.cloudbroker_user_create()
        self.lg('- add user3 to the cloudspace by user2 with read access')
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=user3,
                                    accesstype='R',
                                    api=self.user_api)
    elif operation == 'cloudspaceUpdateuser':
        self.lg('- create account for user3')
        user3 = self.cloudbroker_user_create()
        self.lg('- add user3 to the cloudspace by user2 with read access')
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=user3,
                                    accesstype='R')
        self.lg('- update user3 access on cloudspace by user2 with write access')
        self.user_api.cloudapi.cloudspaces.updateUser(cloudspaceId=self.cloudspace_id,
                                                      userId=user3,
                                                      accesstype='CRX')
        cloudspace = self.api.cloudapi.cloudspaces.get(self.cloudspace_id)
        acl_user3 = [acl for acl in cloudspace['acl'] if acl['userGroupId'] == user3][0]
        self.assertEqual(acl_user3['right'], 'CRX')
    elif operation == 'cloudspaceDeleteuser':
        self.lg('- create account for user3')
        user3 = self.cloudbroker_user_create()
        self.lg('- add user3 to the cloudspace by user2 with read access')
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=user3,
                                    accesstype='R')
        self.lg('- delete cloudspace user: %s with user1' % self.user)
        self.user_api.cloudapi.cloudspaces.deleteUser(cloudspaceId=self.cloudspace_id,
                                                      userId=user3)
    elif operation == 'cloudspaceUpdate':
        self.lg('- create new cloudspace and deploy machine')
        newcloudspaceId = self.cloudapi_cloudspace_create(account_id=self.account_id,
                                                          location=self.location,
                                                          access=self.account_owner,
                                                          api=self.account_owner_api,
                                                          maxMemoryCapacity=512,
                                                          maxDiskCapacity=10)
        self._cloudspaces = [newcloudspaceId]
        self.lg('- deploy new cloudspace')
        self.account_owner_api.cloudapi.cloudspaces.deploy(cloudspaceId=newcloudspaceId)
        self.wait_for_status('DEPLOYED', self.account_owner_api.cloudapi.cloudspaces.get,
                             cloudspaceId=newcloudspaceId)
        self.lg('- update cloudspace name')
        new_cloudspace_name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.user_api.cloudapi.cloudspaces.update(cloudspaceId=newcloudspaceId,
                                                  name=new_cloudspace_name)
        self.lg('- get and verify cloudspace with new name')
        scl = j.clients.osis.getNamespace('cloudbroker')
        cloudspace = scl.cloudspace.get(newcloudspaceId)
        self.assertEqual(cloudspace.name, new_cloudspace_name)
        self.lg('- update cloudspace memory by increase maxMemoryCapacity')
        maxMemoryCapacity = 1024
        self.user_api.cloudapi.cloudspaces.update(cloudspaceId=newcloudspaceId,
                                                  maxMemoryCapacity=maxMemoryCapacity)
        self.lg('- get and verify cloudspace memory')
        cloudspace = scl.cloudspace.get(newcloudspaceId)
        self.assertEqual(cloudspace.resourceLimits['CU_M'], maxMemoryCapacity)
    elif operation == 'cloudspaceDelete':
        self.lg('- create new cloudspace and deploy machine')
        newcloudspaceId = self.cloudapi_cloudspace_create(account_id=self.account_id,
                                                          location=self.location,
                                                          access=self.account_owner,
                                                          api=self.account_owner_api,
                                                          maxMemoryCapacity=512,
                                                          maxDiskCapacity=10)
        self._cloudspaces = [newcloudspaceId]
        self.lg('- deploy new cloudspace')
        self.account_owner_api.cloudapi.cloudspaces.deploy(cloudspaceId=newcloudspaceId)
        self.wait_for_status('DEPLOYED', self.account_owner_api.cloudapi.cloudspaces.get,
                             cloudspaceId=newcloudspaceId)
        self.lg('- delete cloudspace.')
        self.user_api.cloudapi.cloudspaces.delete(cloudspaceId=newcloudspaceId)
        self._cloudspaces.remove(newcloudspaceId)
        cloudspaces = self.account_owner_api.cloudapi.cloudspaces.list()
        self.assertEqual(len(cloudspaces),
                         1,
                         'Should have only the default cloudspace')
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_machine_read(self, operation='machine_get'):
    if operation == 'machine_get':
        machine = self.user_api.cloudapi.machines.get(machineId=self.machine_id)
        self.assertEqual(machine['id'], self.machine_id)
    elif operation == 'machine_list':
        machines = self.user_api.cloudapi.machines.list(cloudspaceId=self.cloudspace_id)
        self.assertEqual(len(machines), 1)
        self.assertEqual(machines[0]['id'], self.machine_id)
    elif operation == 'machine_getConsoleUrl':
        consol_url = self.user_api.cloudapi.machines.getConsoleUrl(machineId=self.machine_id)
        self.assertTrue(consol_url)
    elif operation == 'machine_listSnapshots':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.account_owner_api.cloudapi.machines.snapshot(machineId=self.machine_id,
                                                          name=name)
        snapshots = self.user_api.cloudapi.machines.listSnapshots(machineId=self.machine_id)
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]['name'], name)
    elif operation == 'machine_getHistory':
        for _  in range(10):
            time.sleep(2)
            histories = self.user_api.cloudapi.machines.getHistory(machineId=self.machine_id,
                                                               size=10)

            if histories != []:
                break
        else:
            raise AssertionError('there is no history for vm %s'%self.machine_id)

        self.assertIn('Created', [history['message'] for history in histories])
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_machine_write(self, operation='start_machine'):
    if operation == 'start_machine':
        self.account_owner_api.cloudapi.machines.stop(machineId=self.machine_id)
        self.user_api.cloudapi.machines.start(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'RUNNING')
    elif operation == 'stop_machine':
        self.user_api.cloudapi.machines.stop(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'HALTED')
    elif operation == 'reboot_machine':
        self.user_api.cloudapi.machines.reboot(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'RUNNING')
    elif operation == 'reset_machine':
        self.user_api.cloudapi.machines.reset(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'RUNNING')
    elif operation == 'pause_machine':
        self.user_api.cloudapi.machines.pause(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'PAUSED')
    elif operation == 'resume_machine':
        self.account_owner_api.cloudapi.machines.pause(machineId=self.machine_id)
        self.user_api.cloudapi.machines.resume(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'RUNNING')
    elif operation == 'snapshot_create':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.user_api.cloudapi.machines.snapshot(machineId=self.machine_id,
                                                 name=name)
        snapshots = self.api.cloudapi.machines.listSnapshots(machineId=self.machine_id)
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(name, snapshots[0]['name'])
    elif operation == 'snapshot_rollback':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.account_owner_api.cloudapi.machines.snapshot(machineId=self.machine_id,
                                                          name=name)
        snapshots = self.api.cloudapi.machines.listSnapshots(machineId=self.machine_id)
        self.assertEqual(len(snapshots), 1)
        self.account_owner_api.cloudapi.machines.stop(machineId=self.machine_id)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['status'],
                         'HALTED')
        self.user_api.cloudapi.machines.rollbackSnapshot(machineId=self.machine_id,
                                                         epoch=snapshots[0]['epoch'])
    elif operation == 'snapshot_delete':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.account_owner_api.cloudapi.machines.snapshot(machineId=self.machine_id,
                                                          name=name)
        snapshots = self.api.cloudapi.machines.listSnapshots(machineId=self.machine_id)
        self.assertEqual(len(snapshots), 1)
        self.user_api.cloudapi.machines.deleteSnapshot(machineId=self.machine_id,
                                                       epoch=snapshots[0]['epoch'])

        snapshots = self.api.cloudapi.machines.listSnapshots(machineId=self.machine_id)
        self.assertEqual(len(snapshots), 0)
    elif operation == 'update_machine_name':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.user_api.cloudapi.machines.update(machineId=self.machine_id,
                                               name=name)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['name'],
                         name)
    elif operation == 'update_machine_description':
        name = str(uuid.uuid4()).replace('-', '')[0:10]
        self.user_api.cloudapi.machines.update(machineId=self.machine_id,
                                               description=name)
        self.assertEqual(self.api.cloudapi.machines.get(machineId=self.machine_id)['description'],
                         name)
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)

def try_machine_admin(self, operation='machine_adduser'):
    self.lg('- create account for user3')
    user3 = self.cloudbroker_user_create()
    if operation == 'machine_adduser':
        self.user_api.cloudapi.machines.addUser(machineId=self.machine_id,
                                                userId=user3,
                                                accesstype='R')
        machine = self.api.cloudapi.machines.get(self.machine_id)
        self.assertIn(user3, [acl['userGroupId'] for acl in machine['acl']])
        acl_user3 = [acl for acl in machine['acl'] if acl['userGroupId'] == user3][0]
        self.assertEqual(acl_user3['right'], 'R')
    elif operation == 'machine_updateuser':
        self.account_owner_api.cloudapi.machines.addUser(machineId=self.machine_id,
                                                         userId=user3,
                                                         accesstype='R')
        self.user_api.cloudapi.machines.updateUser(machineId=self.machine_id,
                                                   userId=user3,
                                                   accesstype='CRX')
        machine = self.api.cloudapi.machines.get(self.machine_id)
        self.assertIn(user3, [acl['userGroupId'] for acl in machine['acl']])
        acl_user3 = [acl for acl in machine['acl'] if acl['userGroupId'] == user3][0]
        self.assertEqual(acl_user3['right'], 'CRX')
    elif operation == 'machine_deleteuser':
        self.account_owner_api.cloudapi.machines.addUser(machineId=self.machine_id,
                                                         userId=user3,
                                                         accesstype='R')
        self.user_api.cloudapi.machines.deleteUser(machineId=self.machine_id,
                                                   userId=user3)
        machine = self.api.cloudapi.machines.get(self.machine_id)
        self.assertNotIn(user3, [acl['userGroupId'] for acl in machine['acl']])
    else:
        raise AssertionError('Un-supported operation [%s]' % operation)
