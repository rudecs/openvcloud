from JumpScale import j
import logging
import unittest
import uuid
import time

SESSION_DATA = {'vms':[]}

class API(object):
    API = {}
    def __init__(self):
        self._models = None
        self._portalclient = None
        self._cloudapi = None

    def __getattr__(self, item):
        def set_api(attr):
            API.API[item] = attr
            setattr(self, item, attr)
            return attr

        if item in API.API:
            attr = API.API[item]
            setattr(self, item, attr)
            return attr
        else:
            if item == 'models':
                return set_api(j.clients.osis.getNamespace('cloudbroker'))
            elif item == 'portalclient':
                return set_api(j.clients.portal.getByInstance('main'))
            elif item == 'cloudapi':
                return set_api(self.portalclient.actors.cloudapi)
        raise AttributeError(item)


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.api = API()
        super(BaseTest, self).__init__(*args, **kwargs)

    def get_cloudspace(self):
        if 'cloudspaceid' not in SESSION_DATA:
            cloudspaces = self.api.cloudapi.cloudspaces.list()
            self.assertIsInstance(cloudspaces, list)
            self.assertTrue(cloudspaces)
            SESSION_DATA['cloudspaceid'] = cloudspaces[0]['id']
        return SESSION_DATA['cloudspaceid']

    def waitForStatus(self, vmid, status, timeout=60):
        start = time.time()
        vm = self.api.cloudapi.machines.get(vmid)
        while start + timeout > time.time():
            if vm['status'] == status:
                break
            time.sleep(3)
            logging.info('Checking status %s vs %s',  vm['status'], status)
            vm = self.api.cloudapi.machines.get(vmid)
        self.assertEqual(vm['status'], status)

    def stop_vm(self, vmid):
        self.api.cloudapi.machines.stop(vmid)
        try:
            self.waitForStatus(vmid, 'HALTED', timeout=10)
        except AssertionError:
            self.api.cloudapi.machines.stop(vmid)
            self.waitForStatus(vmid, 'HALTED')

    def get_imageid(self):
        if 'imageid' not in SESSION_DATA:
            images = self.api.cloudapi.images.list()
            self.assertTrue(images)
            SESSION_DATA['imageid'] = images[0]['id']
        return SESSION_DATA['imageid']

    def get_size(self):
        if 'sizeid' not in SESSION_DATA:
            sizes = self.api.cloudapi.sizes.list(cloudspaceId=SESSION_DATA['cloudspaceid'])
            self.assertTrue(sizes)
            SESSION_DATA['sizeid'] = sizes[0]['id']
        return SESSION_DATA['sizeid']

    def create_machine(self):
        vmname = str(uuid.uuid4())
        cloudspaceid = self.get_cloudspace()
        imageid = self.get_imageid()
        sizeid = self.get_size()
        vmid = self.api.cloudapi.machines.create(cloudspaceid, vmname,
                                            'description', sizeid,
                                            imageid, 10)
        self.assertTrue(vmid)
        vmachine = self.api.cloudapi.machines.get(vmid)
        SESSION_DATA.setdefault('vms', []).append(vmachine)
        self.assertEqual(vmachine['status'], 'RUNNING')
        return vmid
