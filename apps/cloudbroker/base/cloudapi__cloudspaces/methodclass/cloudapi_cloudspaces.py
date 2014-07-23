from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator, network
import netaddr
import ujson
import gevent
import urlparse
import uuid


def getIP(network):
    if not network:
        return network
    return str(netaddr.IPNetwork(network).ip)


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
        self.netmgr = j.apps.jumpscale.netmgr
        self.gridid = j.application.config.get('grid.id')
        self.network = network.Network(self.models)

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
    @audit()
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
        if not j.core.portal.active.auth.userExists(userId):
            ctx.start_response('404 Not Found', [])
            return 'Unexisting user'
        else:
            cloudspace = self.models.cloudspace.get(cloudspaceId)
            cs = cloudspace
            acl = cs.new_acl()
            acl.userGroupId = userId
            acl.type = 'U'
            acl.right = accesstype
            return self.models.cloudspace.set(cs)[0]

    @authenticator.auth(acl='A')
    @audit()
    def create(self, accountId, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Create an extra cloudspace
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        result int

        """
        cs = self.models.cloudspace.new()
        cs.name = name
        cs.accountId = accountId
        cs.location = self.cb.extensions.imp.whereAmI()
        ace = cs.new_acl()
        ace.userGroupId = access
        ace.type = 'U'
        ace.right = 'CXDRAU'
        cs.resourceLimits['CU'] = maxMemoryCapacity
        cs.resourceLimits['SU'] = maxDiskCapacity
        cs.status = 'VIRTUAL'
        networkid = self.libvirt_actor.getFreeNetworkId()
        if not networkid:
            raise RuntimeError("Failed to get networkid")

        cs.networkId = networkid
        cs.secret = str(uuid.uuid4())
        cloudspace_id = self.models.cloudspace.set(cs)[0]
        return cloudspace_id

    def _release_resources(self, cloudspace):
         #delete routeros
        fws = self.netmgr.fw_list(self.gridid, str(cloudspace.id))
        if fws:
            self.netmgr.fw_delete(fws[0]['guid'], self.gridid)
        if cloudspace.networkId:
            self.libvirt_actor.releaseNetworkId(cloudspace.networkId)
        if cloudspace.publicipaddress:
            self.network.releasePublicIpAddress(cloudspace.publicipaddress)
        cloudspace.networkId = None
        cloudspace.publicipaddress = None
        return cloudspace

    @authenticator.auth(acl='C')
    def deploy(self, cloudspaceId, **kwargs):
        cs = self.models.cloudspace.get(cloudspaceId)
        if cs.status != 'VIRTUAL':
            return cs.status

        cs.status = 'DEPLOYING'
        self.models.cloudspace.set(cs)
        networkid = cs.networkId
        pool, publicipaddress = self.network.getPublicIpAddress()
        publicgw = pool.gateway
        network = netaddr.IPNetwork(pool.id)
        publiccidr = network.prefixlen
        if not publicipaddress:
            raise RuntimeError("Failed to get publicip for networkid %s" % networkid)

        cs.publicipaddress = str(publicipaddress)
        self.models.cloudspace.set(cs)
        password = str(uuid.uuid4())
        try:
            self.netmgr.fw_create(str(cloudspaceId), 'admin', password, str(publicipaddress.ip), 'routeros', networkid, publicgwip=publicgw, publiccidr=publiccidr)
        except:
            self.network.releasePublicIpAddress(str(publicipaddress))
            cs.status = 'VIRTUAL'
            self.models.cloudspace.set(cs)
            raise
        cs.status = 'DEPLOYED'
        self.models.cloudspace.set(cs)
        return cs.status

    @authenticator.auth(acl='A')
    @audit()
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
        if len(results) == 0:
            ctx.start_response('409 Conflict', [])
            return 'The last CloudSpace of an account can not be deleted.'

        cloudspace.status = "DESTROYING"
        self.models.cloudspace.set(cloudspace)
        cloudspace = self._release_resources(cloudspace)
        cloudspace.status = 'DESTROYED'
        self.models.cloudspace.set(cloudspace)


    @authenticator.auth(acl='R')
    @audit()
    def get(self, cloudspaceId, **kwargs):
        """
        get cloudspaces.
        param:cloudspaceId id of the cloudspace
        result dict
        """
        cloudspaceObject = self.models.cloudspace.get(cloudspaceId)

        #For backwards compatibility, set the secret if it is not filled in
        if len(cloudspaceObject.secret) == 0:
            cloudspaceObject.secret = str(uuid.uuid4())
            self.models.cloudspace.set(cloudspaceObject)

        cloudspace = { "accountId": cloudspaceObject.accountId,
                        "acl": [{"right": acl.right, "type": acl.type, "userGroupId": acl.userGroupId} for acl in cloudspaceObject.acl],
                        "description": cloudspaceObject.descr,
                        "id": cloudspaceObject.id,
                        "name": cloudspaceObject.name,
                        "publicipaddress": getIP(cloudspaceObject.publicipaddress),
                        "status": cloudspaceObject.status,
                        "location": cloudspaceObject.location,
                        "secret": cloudspaceObject.secret}
        return cloudspace

    @authenticator.auth(acl='U')
    @audit()
    def deleteUser(self, cloudspaceId, userId, **kwargs):
        """
        Delete a user from the cloudspace
        params:cloudspaceId id of the cloudspace
        param:userId id of the user to remove
        result

        """
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        change = False
        for ace in cloudspace.acl:
            if ace.userGroupId == userId:
                cloudspace.acl.remove(ace)
                change = True
        if change:
            self.models.cloudspace.set(cloudspace)
        return change

    @audit()
    def list(self, **kwargs):
        """
        List cloudspaces.
        result []
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        query = {'fields': ['id', 'name', 'descr', 'status', 'accountId','acl','publicipaddress','location']}
        query['query'] = {'bool':{'must':[{'term': {'userGroupId': user.lower()}}],'must_not':[{'term':{'status':'DESTROYED'.lower()}}]}}
        results = self.models.cloudspace.find(ujson.dumps(query))['result']
        cloudspaces = [res['fields'] for res in results]

        #during the transitions phase, not all locations might be filled in
        for cloudspace in cloudspaces:
            if not 'location' in cloudspace or len(cloudspace['location']) == 0:
                cloudspace['location'] = self.cb.extensions.imp.whereAmI()

        locations = self.cb.extensions.imp.getLocations()

        for cloudspace in cloudspaces:
            account = self.models.account.get(cloudspace['accountId'])
            cloudspace['publicipaddress'] = getIP(cloudspace['publicipaddress'])
            cloudspace['locationurl'] = locations[cloudspace['location'].lower()]
            cloudspace['accountName'] = account.name
            for acl in account.acl:
                if acl.userGroupId == user.lower() and acl.type == 'U':
                    cloudspace['accountAcl'] = acl
                    cloudspace['userRightsOnAccountBilling'] = True
            cloudspace['accountDCLocation'] = account.DCLocation

        return cloudspaces

    @authenticator.auth(acl='A')
    @audit()
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

    @authenticator.auth(acl='C')
    def getDefenseShield(self, cloudspaceId, **kwargs):
        """
        Get informayion about the defense sheild
        param:cloudspaceId id of the cloudspace
        """
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fwid = "%s_%s" % (j.application.whoAmI.gid, cloudspace.networkId)
        api = self.netmgr.fw_getapi(fwid)
        pwd = str(uuid.uuid4())
        api.executeScript('/user set admin password=%s' %  pwd)
        location = cloudspace.location
        if not location in self.cb.extensions.imp.getLocations():
            location = self.cb.extensions.imp.whereAmI()

        url = 'https://%s.defense.%s.mothership1.com/webfig' % ('-'.join(getIP(cloudspace.publicipaddress).split('.')),location)
        result = {'user': 'admin', 'password': pwd, 'url': url}
        return result
