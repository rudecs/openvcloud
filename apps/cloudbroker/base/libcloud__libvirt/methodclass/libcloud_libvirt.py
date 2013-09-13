from JumpScale import j
from libcloud_libvirt_osis import libcloud_libvirt_osis
import ujson

class libcloud_libvirt(libcloud_libvirt_osis):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="libvirt"
        self.appname="libcloud"
        libcloud_libvirt_osis.__init__(self)
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.libcloud.libvirt
        return self._cb
 

    def listImages(self, **kwargs):
        """
        List the available images
        result  
        """
        term = dict()
        query = {'fields': ['id', 'name', 'description', 'type', 'UNCPath', 'size']}
        results = self.cb.model_image_find(ujson.dumps(query))['result']
        images = [res['fields'] for res in results]
        return images

    

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result  
        
        """
        term = dict()
        query = {'fields': ['id', 'name', 'vcpus', 'memory', 'disk']}
        results = self.cb.model_size_find(ujson.dumps(query))['result']
        sizes = [res['fields'] for res in results]
        return sizes
    
