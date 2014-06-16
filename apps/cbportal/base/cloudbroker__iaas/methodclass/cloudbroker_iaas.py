from JumpScale import j
import JumpScale.grid.osis
json = j.db.serializers.ujson
from JumpScale.portal.portal.auth import auth

class cloudbroker_iaas(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname = "iaas"
        self.appname = "cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    def addPublicIPv4Subnet(self, subnet, **kwargs):
        """
        Adds a public network range to be used for cloudspaces
        param:subnet the subnet to add in CIDR notation (x.x.x.x/y)
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method addPublicIPv4Subnet")

    @auth(['level1', 'level2'])
    def syncAvailableImagesToCloudbroker(self, **kwargs):
        """
        synchronize IaaS Images from the libcloud model and cpunodes to the cloudbroker model
        result boolean
        """
        stacks = self.cbcl.stack.list()
        for stack in stacks:
            self.cb.extensions.imp.stackImportImages(stack)
        return True
