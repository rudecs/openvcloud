from JumpScale import j

class cloudbroker_vmexport_osismodelbase(j.code.classGetJSRootModelBase()):
    """
    A export of a vm. Contains one or multiple files.
    
    """
    def __init__(self):
        self._P_id=0
    
        self._P_vmachineId=0
    
        self._P_type=""
    
        self._P_bucket=""
    
        self._P_server=""
    
        self._P_storagetype=""
    
        self._P_size=0
    
        self._P_timestamp=0
    
        self._P_config=""
    
        self._P_location=""
    
        self._P_files=""
    
        self._P_guid=""
    
        self._P__meta=list()
    
        self._P__meta=["osismodel","cloudbroker","vmexport",1] #@todo version not implemented now, just already foreseen
    

        pass

    @property
    def id(self):
        return self._P_id
    @id.setter
    def id(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property id input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_id=value
    @id.deleter
    def id(self):
        del self._P_id


    @property
    def vmachineId(self):
        return self._P_vmachineId
    @vmachineId.setter
    def vmachineId(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property vmachineId input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_vmachineId=value
    @vmachineId.deleter
    def vmachineId(self):
        del self._P_vmachineId


    @property
    def type(self):
        return self._P_type
    @type.setter
    def type(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property type input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_type=value
    @type.deleter
    def type(self):
        del self._P_type


    @property
    def bucket(self):
        return self._P_bucket
    @bucket.setter
    def bucket(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property bucket input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_bucket=value
    @bucket.deleter
    def bucket(self):
        del self._P_bucket


    @property
    def server(self):
        return self._P_server
    @server.setter
    def server(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property server input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_server=value
    @server.deleter
    def server(self):
        del self._P_server


    @property
    def storagetype(self):
        return self._P_storagetype
    @storagetype.setter
    def storagetype(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property storagetype input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_storagetype=value
    @storagetype.deleter
    def storagetype(self):
        del self._P_storagetype


    @property
    def size(self):
        return self._P_size
    @size.setter
    def size(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property size input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_size=value
    @size.deleter
    def size(self):
        del self._P_size


    @property
    def timestamp(self):
        return self._P_timestamp
    @timestamp.setter
    def timestamp(self, value):
        
        if not isinstance(value, int) and value is not None:
            if isinstance(value, basestring) and j.basetype.integer.checkString(value):
                value = j.basetype.integer.fromString(value)
            else:
                msg="property timestamp input error, needs to be int, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_timestamp=value
    @timestamp.deleter
    def timestamp(self):
        del self._P_timestamp


    @property
    def config(self):
        return self._P_config
    @config.setter
    def config(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property config input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_config=value
    @config.deleter
    def config(self):
        del self._P_config


    @property
    def location(self):
        return self._P_location
    @location.setter
    def location(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property location input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_location=value
    @location.deleter
    def location(self):
        del self._P_location


    @property
    def files(self):
        return self._P_files
    @files.setter
    def files(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property files input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_files=value
    @files.deleter
    def files(self):
        del self._P_files


    @property
    def guid(self):
        return self._P_guid
    @guid.setter
    def guid(self, value):
        
        if not isinstance(value, str) and value is not None:
            if isinstance(value, basestring) and j.basetype.string.checkString(value):
                value = j.basetype.string.fromString(value)
            else:
                msg="property guid input error, needs to be str, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P_guid=value
    @guid.deleter
    def guid(self):
        del self._P_guid


    @property
    def _meta(self):
        return self._P__meta
    @_meta.setter
    def _meta(self, value):
        
        if not isinstance(value, list) and value is not None:
            if isinstance(value, basestring) and j.basetype.list.checkString(value):
                value = j.basetype.list.fromString(value)
            else:
                msg="property _meta input error, needs to be list, specfile: /opt/jumpscale/apps/osis/logic/cloudbroker/model.spec, name model: vmexport, value was:" + str(value)
                raise RuntimeError(msg)
    

        self._P__meta=value
    @_meta.deleter
    def _meta(self):
        del self._P__meta

