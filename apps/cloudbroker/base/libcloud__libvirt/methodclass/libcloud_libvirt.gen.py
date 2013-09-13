from JumpScale import j
from libcloud_libvirt_osis import libcloud_libvirt_osis


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
    

        pass

    def listImages(self, **kwargs):
        """
        List the available images
        result  
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listImages")
    

    def listSizes(self, **kwargs):
        """
        List the available sizes, a size is a combination of compute capacity(memory, cpu) and the disk capacity.
        result  
        
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listSizes")
    
