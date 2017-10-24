from JumpScale import j
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_sizes(BaseActor):
    """
    Lists all the configured flavors available.
    A flavor is a combination of amount of compute capacity(CU) and disk capacity(GB).
    """

    def list(self, cloudspaceId=None, location=None, **kwargs):
        """
        List the available flavors, filtering based on the cloudspace

        :param cloudspaceId: id of the cloudspace
        :return list of flavors contains id CU and disksize for every flavor on the cloudspace
        """
        query = {}
        if not location and not cloudspaceId:
            raise exceptions.BadRequest("Either cloudspaceId or location should be given")
        if location:
            locations = self.models.location.search({'locationCode': location})[1:]
            if not locations:
                raise exceptions.BadRequest("Could not find location with code {}".format(location))
            gid = locations[0]['gid']
        else:
            cloudspace = self.models.cloudspace.get(cloudspaceId)
            if cloudspace.allowedVMSizes:
                query['id'] = {'$in': cloudspace.allowedVMSizes}
            gid = cloudspace.gid
        query['gids'] = gid

        fields = ['id', 'name', 'vcpus', 'memory', 'description', 'CU', 'disks']
        results = self.models.size.search({'$fields': fields, '$query': query})[1:]
        return results
