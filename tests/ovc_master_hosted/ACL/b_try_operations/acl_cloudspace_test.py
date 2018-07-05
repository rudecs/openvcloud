# coding=utf-8
from nose_parameterized import parameterized

from ....utils.utils import BasicACLTest
from ....utils.acl_try_operations import *
from JumpScale.portal.portal.PortalClient2 import ApiError


class ACLCLOUDSPACE(BasicACLTest):

    def setUp(self):
        super(ACLCLOUDSPACE, self).setUp()

        self.acl_setup()


class Read(ACLCLOUDSPACE):


    @parameterized.expand(['get',
                           'list',
                           'getCreditBalance',
                           'getCreditHistory'])
    def test000a_try_account_account_read_operations(self, operation):
        """ ACL-7
        *Test case for try to use read operations read access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try read operation account with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_account_read, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['machine_get',
                           'machine_list',
                           'machine_getConsoleUrl',
                           'machine_listSnapshots',
                           'machine_getHistory'])
    def test000b_try_machine_read_operations(self, operation):
        """ ACL-50
        *Test case for try to use read operations with read access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with admin access
        #. try read operation machine with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_read(self, operation)

    @parameterized.expand(['cloudspaceDeploy',
                           'cloudspaceDefenseshield',
                           'cloudspacePortforwardingAdd',
                           'cloudspacePortforwardingUpdate',
                           'cloudspacePortforwardingDelete',
                           'cloudspaceMachineCreate',
                           'cloudspaceMachineClone',
                           'cloudspaceMachineDelete',
                           'cloudspaceMachineResize'])
    def test001a_try_cloudspace_write_operations(self, operation):
        """ ACL-34
        *Test case for try to use write operations with read access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with read access
        #. try write operation on user2 with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_cloudspace_write, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['start_machine',
                           'stop_machine',
                           'reboot_machine',
                           'reset_machine',
                           'pause_machine',
                           'resume_machine',
                           'snapshot_create',
                           'snapshot_rollback',
                           'snapshot_delete',
                           'update_machine_name',
                           'update_machine_description'])
    def test001b_try_machine_write_operations(self, operation):
        """ ACL-46
        *Test case for try to use write operations with read access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with read access
        #. try write operation on user2 with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_machine_write, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['cloudspaceAdduser',
                           'cloudspaceUpdateuser',
                           'cloudspaceDeleteuser',
                           'cloudspaceUpdate',
                           'cloudspaceDelete'])
    def test002a_try_cloudspace_admin_operations(self, operation):
        """ ACL-35
        *Test case for try to use admin operations with read access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with read access
        #. try admin operation with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_cloudspace_admin, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['machine_adduser',
                           'machine_updateuser',
                           'machine_deleteuser'])
    def test002b_try_machine_admin_operations(self, operation):
        """ ACL-47
        *Test case for try to use admin operations with read access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with read access
        #. try admin operation with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'R'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_machine_admin, self, operation)

        self.lg('%s ENDED' % self._testID)


class Write(ACLCLOUDSPACE):

    @parameterized.expand(['create_cloudspace',
                           'create_machineTemplate'
                           ])
    def test000a_try_account_write_operations(self, operation):
        """ ACL-1
        *Test case for try to use write operations with write access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try write operation on user2 with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_account_write, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['start_machine',
                           'stop_machine',
                           'reboot_machine',
                           'reset_machine',
                           'pause_machine',
                           'resume_machine',
                           'snapshot_create',
                           'snapshot_rollback',
                           'snapshot_delete',
                           'update_machine_name',
                           'update_machine_description'])
    def test000b_try_machine_write_operations(self, operation):
        """ ACL-51
        *Test case for try to use write operations with write access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try write operation on user2 with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_write(self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['getCloudspace',
                           'listCloudspaces',
                           'listMachines',
                           'listPortforwarding'])
    def test001a_try_cloudspace_read_operations(self, operation):
        """ ACL-36
        *Test case for try to use read operations with write access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try read operation cloudspace with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_cloudspace_read(self, operation)

        self.lg('%s ENDED' % self._testID)


    @parameterized.expand(['machine_get',
                           'machine_list',
                           'machine_getConsoleUrl',
                           'machine_listSnapshots',
                           'machine_getHistory'])
    def test001b_try_machine_read_operations(self, operation):
        """ ACL-48
        *Test case for try to use read operations with write access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try read operation machine with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_read(self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['cloudspaceAdduser',
                           'cloudspaceUpdateuser',
                           'cloudspaceDeleteuser',
                           'cloudspaceUpdate',
                           'cloudspaceDelete'])
    def test002a_try_cloudspace_admin_operations(self, operation):
        """ ACL-37
        *Test case for try to use admin operations with write access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try admin operation with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_cloudspace_admin, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['machine_adduser',
                           'machine_updateuser',
                           'machine_deleteuser'])
    def test002b_try_machine_admin_operations(self, operation):
        """ ACL-49
        *Test case for try to use admin operations with write access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try admin operation with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'CRX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_admin(self, operation)

        self.lg('%s ENDED' % self._testID)


class Admin(ACLCLOUDSPACE):

    @parameterized.expand(['add_user',
                           'update',
                           'delete_user'])
    def test000a_try_account_admin_operations(self, operation):
        """ ACL-2
        *Test case for try to use admin operations with admin access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with read access
        #. try admin operation with user1, should fail '403 Forbidden'
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        self.assertRaises(ApiError, try_account_admin, self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['machine_adduser',
                           'machine_updateuser',
                           'machine_deleteuser'])
    def test000b_try_machine_admin_operations(self, operation):
        """ ACL-49
        *Test case for try to use admin operations with admin access, on upper level.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with write access
        #. try admin operation with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_admin(self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['getCloudspace',
                           'listCloudspaces',
                           'listMachines',
                           'listPortforwarding'])
    def test001a_try_cloudspace_read_operations(self, operation):
        """ ACL-38
        *Test case for try to use read operations with admin access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with admin access
        #. try read operation cloudspace with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_cloudspace_read(self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['machine_get',
                           'machine_list',
                           'machine_getConsoleUrl',
                           'machine_listSnapshots',
                           'machine_getHistory'])
    def test001b_try_machine_read_operations(self, operation):
        """ ACL-50
        *Test case for try to use read operations with admin access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with admin access
        #. try read operation machine with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_read(self, operation)

        self.lg('%s ENDED' % self._testID)

    @parameterized.expand(['cloudspaceDeploy',
                           'cloudspaceDefenseshield',
                           'cloudspacePortforwardingAdd',
                           'cloudspacePortforwardingUpdate',
                           'cloudspacePortforwardingDelete',
                           'cloudspaceMachineCreate',
                           #'cloudspaceMachineClone',
                           #skip("https://github.com/0-complexity/openvcloud/issues/745")
                           'cloudspaceMachineDelete',
                           'cloudspaceMachineResize'])
    def test002a_try_cloudspace_write_operations(self, operation):
        """ ACL-39
        *Test case for try to use write operations with admin access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with admin access
        #. try write operation on user2 with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_cloudspace_write(self, operation)

        self.lg('%s ENDED' % self._testID)


    @parameterized.expand(['start_machine',
                           'stop_machine',
                           'reboot_machine',
                           'reset_machine',
                           'pause_machine',
                           'resume_machine',
                           'snapshot_create',
                           'snapshot_rollback',
                           'snapshot_delete',
                           'update_machine_name',
                           'update_machine_description'])
    def test002b_try_machine_write_operations(self, operation):
        """ ACL-51
        *Test case for try to use write operations with admin access.*

        **Test Scenario:**

        #. add user1 to the cloudspace created by user2 with admin access
        #. try write operation on user2 with user1, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.machine_id = self.cloudapi_create_machine(self.cloudspace_id,
                                                       self.account_owner_api)
        accesstype = 'ACDRUX'
        self.lg('- add user1 to the cloudspace owned by user2 with access type [%s]' % accesstype)
        self.add_user_to_cloudspace(cloudspace_id=self.cloudspace_id,
                                    user=self.user,
                                    accesstype=accesstype)
        try_machine_write(self, operation)

        self.lg('%s ENDED' % self._testID)

