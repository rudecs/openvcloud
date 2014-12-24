from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_images(BaseActor):
    """
    Lists all the images. A image is a template which can be used to deploy machines.

    """
    @audit()
    def list(self, accountid, cloudspaceid, **kwargs):
        """
        List the availabe images, filtering can be based on the cloudspace and the user which is doing the request
        """
        fields = ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        if accountid:
            q = {'status': 'CREATED', 'accountId': int(accountid)}
        else:
            q = {'status': 'CREATED', 'accountId': 0}
        query = {'$query': q, '$fields': fields}
        results = self.models.image.search(query)[1:]

        if cloudspaceid:
            cloudspace = self.models.cloudspace.get(int(cloudspaceid))
            if cloudspace:
                stacks = self.models.stack.search({'gid': cloudspace.gid})[1:]
                imageids = list()
                for stack in stacks:
                    for id in stack['images']:
                        if id not in imageids:
                            imageids.append(id)
                if len(imageids) > 0:
                    images = self.models.image.search({'id': {'$in': imageids}})[1:]
                    if len(images) > 0:
                        results.extend(images)

        return results

    @audit()
    def delete(self, imageid, **kwargs):
        """
        Delete a image, you need to have Write access on the image
        param:imageid id of the image to delete
        result
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method delete")

