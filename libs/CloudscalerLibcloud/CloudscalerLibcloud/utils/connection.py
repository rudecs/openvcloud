import md5


class DummyConnection():

    def listSizes(self):
        sizes = [{'memory': '1750', 'vcpus': 1, 'disk': 40, 'guid':
                  '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 1, 'name': u'BIG',
                  'referenceId': ''}, {'memory': '3600', 'vcpus': 2, 'disk': 20, 'guid':
                                       '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 2, 'name': u'SMALL',
                                       'referenceId': ''}]
        return sizes

    def listImages(self):
        images = [{'UNCPath': 'vmhendrik.img',
                   'description': '',
                   'guid': '3c655a10-7e04-4d93-8ea1-ec5536d9689b',
                   'id': 1,
                   'name': 'ubuntu-2',
                   'referenceId': '',
                   'size': 10,
                   'type': 'ubuntu'}, {'UNCPath': 'file:///ISOS/windows-2008.iso',
                                       'description': '',
                                       'guid': '3c655a10-7e04-4d93-8ea1-ec5536d9689b',
                                       'id': 2,
                                       'name': 'windows-2008',
                                       'referenceId': '',
                                       'size': 20,
                                       'type': 'WINDOWS'}]
        return images


class CloudBrokerConnection():
    NAMESPACE = 'libcloud'
    CATEGORY = 'libvirtdomain'

    def __init__(self, client=None):
        from JumpScale import j
        self._j = j
        import JumpScale.grid.geventws
        from JumpScale.grid import agentcontroller
        if client:
            self.client = client
            self.libvirt_actor = self.client.getActor('libcloud', 'libvirt')
        else:
            self.libvirt_actor = j.apps.libcloud.libvirt
        self.db = self._getKeyValueStore()
        self.agentcontroller_client = j.clients.agentcontroller.get()

    def _getKeyValueStore(self):
        import JumpScale.grid.osis
        client = self._j.clients.osis.getByInstance('main')
        if self.NAMESPACE not in client.listNamespaces():
            client.createNamespace(self.NAMESPACE, 'blob')
        if self.CATEGORY not in client.listNamespaceCategories(self.NAMESPACE):
            client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
        return self._j.clients.osis.getCategory(client, self.NAMESPACE, self.CATEGORY)

    def listSizes(self):
        return self.libvirt_actor.listSizes()

    def listImages(self, id=None):
        if id:
            return self.libvirt_actor.listImages(id)
        return self.libvirt_actor.listImages()

    def listNodes(self):
        return self.libvirt_actor.listNodes()

    def getNode(self, id):
        return self.libvirt_actor.getNode(id)

    def getMacAddress(self, gid):
        return self.libvirt_actor.getFreeMacAddress(gid)

    def registerMachine(self, id, macaddress, networkid):
        return self.libvirt_actor.registerNode(id, macaddress, networkid)

    def unregisterMachine(self, id):
        return self.libvirt_actor.unregisterNode(id)

    def retreiveInfo(self, key):
        return self.libvirt_actor.retreiveInfo(key)

    def storeInfo(self, data, timeout):
        return self.libvirt_actor.storeInfo(data, timeout)

    def listVNC(self, gid):
        return self.libvirt_actor.listVNC(gid)
