from JumpScale import j

OsisBaseObject=j.core.osis.getOSISBaseObjectComplexType()

from vfw_virtualfirewall_osismodelbase import vfw_virtualfirewall_osismodelbase

#this class is meant to be overrided e.g. the getuniquekey, ...

class vfw_virtualfirewall(OsisBaseObject,vfw_virtualfirewall_osismodelbase):

    """
    """

    def __init__(self, ddict={}):
        # OsisBaseObject.__init__(self)
        vfw_virtualfirewall_osismodelbase.__init__(self)
        if ddict <> {}:
            self.load(ddict)

    def getSetGuid(self):
        self.guid = "%s_%s"%(self.gid,self.id)
        self.moddate=j.base.time.getTimeEpoch() 
        return self.guid

    # def getDictForIndex(self):
    #     """
    #     return dict which needs to be indexed
    #     """
    #     pass


