from OpenWizzy import o
from cloudapi_sizes_osis import cloudapi_sizes_osis


class cloudapi_sizes(cloudapi_sizes_osis):

    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).

    """

    def __init__(self):

        self._te = {}
        self.actorname = "sizes"
        self.appname = "cloudapi"
        cloudapi_sizes_osis.__init__(self)

        pass

    def list(self, **kwargs):
        """
        List the availabe flavors, filtering can be based on the user which is doing the request
        result list

        """
        # put your code here to implement this method
        return o.apps.cloud.cloudbroker.model_size_list()
