from JumpScale import j
from cloudbrokerlib import authenticator
import ujson


class cloudapi_cloudspaces(object):
    """
    API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces

    """
    def __init__(self):
        self._te = {}
        self.actorname = "cloudspaces"
        self.appname = "cloudapi"
        self._cb = None
        self._models = None
        self.libvirt_actor = j.apps.libcloud.libvirt 

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models


    @authenticator.auth(acl='U')
    def addUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        params:cloudspaceId id of the cloudspace
        param:userId id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool

        """
        
        ctx = kwargs['ctx']
        if not j.apps.system.usermanager.userexists(userId):
            ctx.start_response('404 Not Found', [])
        else:
            cs = self.cb.models.cloudspace.new()
            cloudspace = self.models.cloudspace.get(cloudspaceId)
            cs.dict2obj(cloudspace)
            acl = cs.new_acl()
            acl.userGroupId = userId
            acl.type = 'U'
            acl.right = accesstype
            return self.models.cloudspace.set(cs)[0]

    @authenticator.auth(acl='A')
    def create(self, accountId, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Create a extra cloudspace
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        result int

        """
        networkid = self.libvirt_actor.getFreeNetworkId()
        publicipaddress = self.cb.extensions.imp.getPublicIpAddress(networkid)
        cs = self.cb.models.cloudspace.new()
        cs.name = name
        cs.accountId = accountId
        ace = cs.new_acl()
        ace.userGroupId = access
        ace.type = 'U'
        ace.right = 'CXDRAU'
        cs.resourceLimits['CU'] = maxMemoryCapacity
        cs.resourceLimits['SU'] = maxDiskCapacity
        cs.networkId = networkid
        cs.publicipaddress = publicipaddress
        return self.models.cloudspace.set(cs)[0]

    @authenticator.auth(acl='A')
    def delete(self, cloudspaceId, **kwargs):
        """
        Delete a cloudspace.
        param:cloudspaceId id of the cloudspace
        result bool,

        """
        ctx = kwargs['ctx']
        #A cloudspace may not contain any resources any more
        query = {'fields': ['id', 'name']}
        query['query'] = {'bool':{'must':[
                                          {'term': {'cloudspaceId': cloudspaceId}}
                                          ],
                                  'must_not':[
                                              {'term':{'status':'DESTROYED'.lower()}}
                                              ]
                                  }
                          }
        results = self.models.vmachine.find(ujson.dumps(query))['result']
        if len(results) > 0:
            ctx.start_response('409 Conflict', [])
            return 'In order to delete a CloudSpace it can not contain Machine Buckets.'
        #The last cloudspace in a space may not be deleted
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        query = {'fields': ['id', 'name']}
        query['query'] = {'bool':{'must':[
                                          {'term': {'accountId': cloudspace.accountId}}
                                          ],
                                  'must_not':[
                                              {'term':{'status':'DESTROYED'.lower()}},
                                              {'term':{'id':cloudspaceId}}
                                              ]
                                  }
                          }
        results = self.models.cloudspace.find(ujson.dumps(query))['result']
        if len(results) > 0:
            ctx.start_response('409 Conflict', [])
            return 'The last CloudSpace of an account can not be deleted.'
        
        cloudspace.status = 'DESTROYED'
        #TODO: remove this
        self.libvirt_actor.releaseNetworkId(cloudspace.networkid)
        
        self.models.cloudspace.set(cloudspace)


    def get(self, cloudspaceId, **kwargs):
        """
        get cloudspaces.
        param:cloudspaceId id of the cloudspace
        result dict
        """
        #put your code here to implement this method
        return self.models.cloudspace.get(cloudspaceId)

    @authenticator.auth(acl='U')
    def deleteUser(self, cloudspaceId, userId, **kwargs):
        """
        Delete a user from the cloudspace
        params:cloudspaceId id of the cloudspace
        param:userId id of the user to remove
        result

        """
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        change = False
        for ace in cloudspace['acl'][:]:
            if ace['userGroupId'] == userId:
                cloudspace['acl'].remove(ace)
                change = True
        if change:
            self.models.cloudspace.set(cloudspace)
        return change

    def list(self, **kwargs):
        """
        List cloudspaces.
        result []
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        query = {'fields': ['id', 'name', 'descr', 'accountId','acl','publicipaddress']}
        query['query'] = {'term': {"userGroupId": user}}
        results = self.models.cloudspace.find(ujson.dumps(query))['result']
        cloudspaces = [res['fields'] for res in results]
        return cloudspaces

    @authenticator.auth(acl='A')
    def update(self, cloudspaceId, name, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Update a cloudspace name and capacity parameters can be updated
        param:cloudspaceId id of the cloudspace to change
        param:name name of the cloudspace
        param:maxMemoryCapacity max size of memory in space(in GB)
        param:maxDiskCapacity max size of aggregated disks(in GB)
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method update")
