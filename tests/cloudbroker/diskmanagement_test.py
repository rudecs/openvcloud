from JumpScale import j
import unittest
from JumpScale.baselib.http_client.HttpClient import HTTPError
from lib import helper

CLEANUP = []

class DiskManagementTest(helper.BaseTest):
    sourcevm = None
    targetvm = None
    diskid = None

    def __init__(self, *args, **kwargs):
        super(DiskManagementTest, self).__init__(*args, **kwargs)

    def assertDiskInVM(self, vmid):
        vmachine = self.api.cloudapi.machines.get(vmid)
        diskids = [disk['id'] for disk in vmachine['disks']]
        self.assertIn(self.diskid, diskids)

    def assertDiskNotInVM(self, vmid):
        vmachine = self.api.cloudapi.machines.get(vmid)
        diskids = [disk['id'] for disk in vmachine['disks']]
        self.assertNotIn(self.diskid, diskids)

    def test_1_addisk(self):
        DiskManagementTest.sourcevm = self.create_machine()
        CLEANUP.append(self.sourcevm)
        with self.assertRaises(HTTPError) as error:
            self.api.cloudapi.machines.addDisk(self.sourcevm, 'diskname', 'description', 10, 'B')
        self.assertEqual(error.exception.status_code, 409)
        self.stop_vm(self.sourcevm)
        DiskManagementTest.diskid = self.api.cloudapi.machines.addDisk(self.sourcevm, 'diskname', 'description', 10, 'B')
        self.assertTrue(self.diskid)
        self.assertTrue(self.api.models.disk.exists(self.diskid))
        self.assertDiskInVM(self.sourcevm)

    def test_2_movedisk(self):
        self.assertTrue(self.diskid, "Requires disk")
        DiskManagementTest.targetvm = self.create_machine()
        CLEANUP.append(self.targetvm)
        with self.assertRaises(HTTPError) as error:
            self.api.cloudapi.machines.attachDisk(self.targetvm, self.diskid)
        self.assertEqual(error.exception.status_code, 409)
        self.stop_vm(self.targetvm)
        self.api.cloudapi.machines.attachDisk(self.targetvm, self.diskid)
        self.assertDiskInVM(self.targetvm)

    def test_3_deletedisk(self):
        self.assertTrue(self.diskid, "Requires disk")
        with self.assertRaises(HTTPError) as error:
            self.api.cloudapi.disks.delete(self.diskid)
        self.assertEqual(error.exception.status_code, 409)
        self.api.cloudapi.disks.delete(self.diskid, True)
        self.assertDiskNotInVM(self.targetvm)


def tearDown():
    api = helper.API()
    for vm in CLEANUP:
        api.cloudapi.machines.delete(vm)


if __name__ == '__main__':
    unittest.main()
