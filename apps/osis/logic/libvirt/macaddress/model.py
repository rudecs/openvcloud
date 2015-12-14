from JumpScale import j
OsisBaseObject=j.core.osis.getOSISBaseObjectComplexType()
from libvirt_node_osismodelbase import libvirt_node_osismodelbase
class libvirt_node(OsisBaseObject,libvirt_node_osismodelbase):

    """
    """

    def __init__(self, ddict={}):
        # OsisBaseObject.__init__(self)
        libvirt_node_osismodelbase.__init__(self)
        if ddict <> {}:
            self.load(ddict)
