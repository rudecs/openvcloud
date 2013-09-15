from JumpScale import j

class libcloud_libvirt_osis(j.code.classGetBase()):
    """
    libvirt libcloud manager.
    Contains function to access the internal model.
    
    """
    def __init__(self):
        self.dbmem=j.db.keyvaluestore.getMemoryStore()
        self.db=self.dbmem
    

        pass

    def model_image_create(self, name, description, UNCPath, size, type, referenceId, **kwargs):
        """
        Create a new model
        param:name name of the image
        param:description extra description of the image
        param:UNCPath location of the image (uncpath like used in pylabs); includes the login/passwd info
        param:size size in MByte
        param:type dot separated list of independant terms known terms are: tar;gz;sso e.g. sso dump inn tar.gz format would be sso.tar.gz  (always in lcas)
        param:referenceId Name of the image on stack
        result json 
        
        """
        
        image = self.models.image.new()
        image.name = name
        image.description = description
        image.UNCPath = UNCPath
        image.size = size
        image.type = type
        image.referenceId = referenceId
        
        return self.models.image.set(image)
                
    

    def model_image_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.image.datatables() #@todo
                    
    

    def model_image_delete(self, id, guid='', **kwargs):
        """
        remove the model image with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.image.delete(guid=guid, id=id)
                    
    

    def model_image_find(self, query='', **kwargs):
        """
        query to model image
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.image.find(query)            
                    
    

    def model_image_get(self, id, guid='', **kwargs):
        """
        get model image with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.image.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_image_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.image.list()            
                    
    

    def model_image_new(self, **kwargs):
        """
        Create a new modelobjectimage instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.image.new()
                    
    

    def model_image_set(self, data='', **kwargs):
        """
        Saves model image instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.image.set(data)            
                    
    

    def model_size_create(self, name, memory, vcpus, disk, **kwargs):
        """
        Create a new model
        param:name Public name of the size
        param:memory Memory in Mb
        param:vcpus Number of virtual cpus assigned to the machine
        param:disk disk size in GB
        result json 
        
        """
        
        size = self.models.size.new()
        size.name = name
        size.memory = memory
        size.vcpus = vcpus
        size.disk = disk
        
        return self.models.size.set(size)
                
    

    def model_size_datatables(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.size.datatables() #@todo
                    
    

    def model_size_delete(self, id, guid='', **kwargs):
        """
        remove the model size with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result bool 
        
        """
        
        return self.models.size.delete(guid=guid, id=id)
                    
    

    def model_size_find(self, query='', **kwargs):
        """
        query to model size
        @todo how to query
        example: name=aname
        secret key needs to be given
        param:query unique identifier can be used as auth key default=
        result list 
        
        """
        
        return self.models.size.find(query)            
                    
    

    def model_size_get(self, id, guid='', **kwargs):
        """
        get model size with specified id and optionally guid
        if secret key is given then guid is not needed, other guid is authentication key
        param:id Object identifier
        param:guid unique identifier can be used as auth key default=
        result object 
        
        """
        
        obj = self.models.size.get(id=id,guid=guid).obj2dict()
        obj.pop('_meta', None)
        return obj
                    
    

    def model_size_list(self, **kwargs):
        """
        list models, used by e.g. a datagrid
        result json 
        
        """
        
        return self.models.size.list()            
                    
    

    def model_size_new(self, **kwargs):
        """
        Create a new modelobjectsize instance and return as empty.
        A new object will be created and a new id & guid generated
        result object 
        
        """
        
        return self.models.size.new()
                    
    

    def model_size_set(self, data='', **kwargs):
        """
        Saves model size instance starting from an existing pymodel object (data is serialized as json dict if required e.g. over rest)
        param:data data is object to save default=
        result bool 
        
        """
        
        return self.models.size.set(data)            
                    
    
