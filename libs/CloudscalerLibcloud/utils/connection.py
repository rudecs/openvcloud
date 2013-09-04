class DummyConnection():
    
    def listSizes(self):
        sizes = [{'CU': 2, 'disks': 40, 'guid':
            '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 1, 'name': u'BIG',
            'referenceId': ''},{'CU': 1, 'disks': 20, 'guid':
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

     def __init__(self, ipaddress=None, port=None, secret=None):
         from JumpScale import j
         import JumpScale.portal
         if ipaddress:
             self.client = j.core.portal.getPortalClient(ip=ipaddress, port=port, secret=secret)  
             self.size_actor = self.client.getActor('cloudapi', 'sizes')
             self.image_actor = self.client.getActor('cloudapi', 'images')
         else:
             self.size_actor = j.apps.cloudapi.sizes
             self.image_actor = j.apps.cloudapi.images
         
     def listSizes(self):
         return self.size_actor.list()

     def listImages(self):
         return self.image_actor.list()
     






