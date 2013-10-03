from JumpScale import j
from cloud_cloudbroker_osis import cloud_cloudbroker_osis
json = j.db.serializers.ujson


class cloud_cloudbroker(cloud_cloudbroker_osis):

    """
    iaas manager

    """

    def __init__(self):

        self._te = {}
        self.actorname = "cloudbroker"
        self.appname = "cloud"
        cloud_cloudbroker_osis.__init__(self)

        pass

  
