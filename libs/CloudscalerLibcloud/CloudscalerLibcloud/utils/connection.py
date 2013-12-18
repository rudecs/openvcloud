import md5

class DummyConnection():
    
    def listSizes(self):
        sizes = [{'memory': '1750', 'vcpus': 1, 'disk': 40, 'guid':
            '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 1, 'name': u'BIG',
            'referenceId': ''},{'memory': '3600', 'vcpus': 2, 'disk': 20, 'guid':
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

     def __init__(self, ipaddress=None, port=None, secret=None):
         from JumpScale import j
         self._j = j
         import JumpScale.portal
         import JumpScale.grid.geventws
         if ipaddress:
             self.client = j.core.portal.getPortalClient(ip=ipaddress, port=port, secret=secret)  
             self.libvirt_actor = self.client.getActor('libcloud', 'libvirt')
         else:
             self.libvirt_actor = j.apps.libcloud.libvirt
         hrd = j.core.hrd.getHRD('/opt/jumpscale/cfg/hrd/')
         self.environmentid = hrd.get('cloudscalers.environmentid')
         self.publicdnsmasqconfigpath = j.system.fs.joinPaths(j.dirs.varDir, 'vxlan', self.environmentid)
         self.db = self._getKeyValueStore()
         login = j.application.config.get('system.superadmin.login')
         passwd = j.application.config.get('system.superadmin.passwd')
         self.agentcontroller_client = j.servers.geventws.getClient("127.0.0.1", 4444, org="myorg", user=login, passwd=passwd, roles=["system.1", "hypervisor.1"],category="agent")


     def _getKeyValueStore(self):
         import JumpScale.grid.osis
         client = self._j.core.osis.getClient()
         if self.NAMESPACE not in client.listNamespaces():
             client.createNamespace(self.NAMESPACE, 'blob')
         if self.CATEGORY not in client.listNamespaceCategories(self.NAMESPACE):
            client.createNamespaceCategory(self.NAMESPACE, self.CATEGORY)
         return self._j.core.osis.getClientForCategory(client, self.NAMESPACE, self.CATEGORY)

     def listSizes(self):
         return self.libvirt_actor.listSizes()

     def listImages(self, id=None):
         if id:
            return self.libvirt_actor.listImages(id)
         return self.libvirt_actor.listImages()

     def listNodes(self):
         return self.libvirt_actor.listNodes()

     def getNode(self,id):
         return self.libvirt_actor.model_node_get(id)

     def getMacAddress(self):
         return self.libvirt_actor.getFreeMacAddress()

     def registerMachine(self, id, macaddress):
         return self.libvirt_actor.registerNode(id, macaddress)

     def unregisterMachine(self, id):
         return self.libvirt_actor.unregisterNode(id)

     def retreiveInfo(self, key):
         return self.libvirt_actor.retreiveInfo(key)

     def storeInfo(self, data, timeout):
         return self.libvirt_actor.storeInfo(data, timeout)

     def listVNC(self):
         return self.libvirt_actor.listVNC()
