from JumpScale import j

OsisBaseObject=j.core.osis.getOSISBaseObjectComplexType()

from $modelbase_osismodelbase import $modelbase_osismodelbase

#this class is meant to be overrided e.g. the getuniquekey, ...

class $modelbase(OsisBaseObject,$modelbase_osismodelbase):

    """
    """

    def __init__(self, ddict={}):
        # OsisBaseObject.__init__(self)
        $modelbase_osismodelbase.__init__(self)
        if ddict <> {}:
            self.load(ddict)


    # def getContentKey(self):
    #     """
    #     this is used to define which fields make to update object in osis, e.g. not all fields are relevant for this and only when relevant ones change it will be stored in db
    #     """
    #     C="%s_%s_%s_%s_%s_%s_%s"%(self.gid,self.nid,self.id,self.name,self.mac,self.ipaddr,self.active)
    #     return j.tools.hash.md5_string(C)

    # def getUniqueKey(self):
    #     """
    #     return unique key for object, is used to define unique id (std the guid)
    #     """
    #     return self.getSetGuid()

    # def getSetGuid(self):
    #     """
    #     use osis to define & set unique guid (sometimes also id)
    #     """
    #     self.gid = int(self.gid)
    #     self.id = int(self.id)

    #     # self.sguid=struct.pack("<HH",self.gid,self.id)
    #     self.guid = "%s_%s" % (self.gid, self.id)
    #     self.lastcheck=j.base.time.getTimeEpoch() 

    #     return self.guid

    # def getDictForIndex(self):
    #     """
    #     return dict which needs to be indexed
    #     """
    #     pass


