from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator, network
from billingenginelib import account as accountbilling
from billingenginelib import pricing
from cloudbrokerlib.baseactor import BaseActor
import netaddr
import uuid
import time


def getIP(network):
    if not network:
        return network
    return str(netaddr.IPNetwork(network).ip)


class cloudapi_cloudspaces(BaseActor):
    """
    API Actor api for managing cloudspaces, this actor is the final api a enduser uses to manage cloudspaces

    """
    def __init__(self):
        super(cloudapi_cloudspaces, self).__init__()
        self.libvirt_actor = j.apps.libcloud.libvirt
        self.netmgr = j.apps.jumpscale.netmgr
        self.network = network.Network(self.models)
        self._accountbilling = accountbilling.account()
        self._pricing = pricing.pricing()
        self._minimum_days_of_credit_required = float(self.hrd.get("mothership1.cloudbroker.creditcheck.daysofcreditrequired"))

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
        cloudspaceId = int(cloudspaceId)
        ctx = kwargs['ctx']
        if not j.core.portal.active.auth.userExists(userId):
            ctx.start_response('404 Not Found', [])
            return 'Unexisting user'
        else:
            cloudspace = self.models.cloudspace.get(cloudspaceId)
            for ace in cloudspace.acl:
                if ace.userGroupId == userId:
                    ace.right = accesstype
                    return self.models.cloudspace.set(cloudspace)[0]
            acl = cloudspace.new_acl()
            acl.userGroupId = userId
            acl.type = 'U'
            acl.right = accesstype
            return self.models.cloudspace.set(cloudspace)[0]

    @authenticator.auth(acl='U')
    @audit()
    def updateUser(self, cloudspaceId, userId, accesstype, **kwargs):
        """
        Updates a user access rights.
        Access rights can be 'R' or 'W'
        params:cloudspaceId id of the cloudspace
        param:userId id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        return self.addUser(cloudspaceId, userId, accesstype)

    def _listActiveCloudSpaces(self, accountId):
        account = self.models.account.get(accountId)
        if account.status == 'DISABLED':
            return []
        query = {'accountId': accountId, 'status': {'$ne': 'DESTROYED'}}
        results = self.models.cloudspace.search(query)[1:]
        return results

    @authenticator.auth(acl='A')
    @audit()
    def create(self, accountId, location, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        Create an extra cloudspace
        param:name name of space to create
        param:access id of user which has full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        result int

        """
        accountId = int(accountId)
        locations = self.models.location.search({'locationCode': location})[1:]
        if not locations:
            ctx = kwargs['ctx']
            ctx.start_response('400 Bad Request', [])
            return 'Location %s does not exists' % location
        location = locations[0]
       

        active_cloudspaces = self._listActiveCloudSpaces(accountId)
        # Extra cloudspaces require a payment and a credit check
        if (len(active_cloudspaces) > 0):
            ctx = kwargs['ctx']
            if (not self._accountbilling.isPayingCustomer(accountId)):
               ctx.start_response('409 Conflict', [])
               return 'Creating an extra cloudspace is only available if you made at least 1 payment'
 
            available_credit = self._accountbilling.getCreditBalance(accountId)
            burnrate = self._pricing.get_burn_rate(accountId)['hourlyCost']
            new_burnrate = burnrate + self._pricing.get_cloudspace_price_per_hour()
            if available_credit < (new_burnrate * 24 * self._minimum_days_of_credit_required):
                ctx.start_response('409 Conflict', [])
                return 'Not enough credit to hold this cloudspace for %i days' % self._minimum_days_of_credit_required

        cs = self.models.cloudspace.new()
        cs.name = name
        cs.accountId = accountId
        cs.location = location['locationCode']
        cs.gid = location['gid']
        ace = cs.new_acl()
        ace.userGroupId = access
        ace.type = 'U'
        ace.right = 'CXDRAU'
        cs.resourceLimits['CU'] = maxMemoryCapacity
        cs.resourceLimits['SU'] = maxDiskCapacity
        cs.status = 'VIRTUAL'
        networkid = self.libvirt_actor.getFreeNetworkId(cs.gid)
        if not networkid:
            raise RuntimeError("Failed to get networkid")

        cs.networkId = networkid
        cs.secret = str(uuid.uuid4())
        cs.creationTime = int(time.time())
        cloudspace_id = self.models.cloudspace.set(cs)[0]
        return cloudspace_id

    def _release_resources(self, cloudspace):
         #delete routeros
        fws = self.netmgr.fw_list(cloudspace.gid, str(cloudspace.id))
        if fws:
            self.netmgr.fw_delete(fws[0]['guid'], cloudspace.gid)
        if cloudspace.networkId:
            self.libvirt_actor.releaseNetworkId(cloudspace.gid, cloudspace.networkId)
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
        netinfo = self.network.getPublicIpAddress(cs.gid)
        if netinfo is None:
            cs.status = 'VIRTUAL'
            self.models.cloudspace.set(cs)
            raise RuntimeError("No available public IPAddresses")
        pool, publicipaddress = netinfo
        publicgw = pool.gateway
        network = netaddr.IPNetwork(pool.id)
        publiccidr = network.prefixlen
        if not publicipaddress:
            raise RuntimeError("Failed to get publicip for networkid %s" % networkid)

        cs.publicipaddress = str(publicipaddress)
        self.models.cloudspace.set(cs)
        password = str(uuid.uuid4())
        try:
            self.netmgr.fw_create(cs.gid, str(cloudspaceId), 'admin', password, str(publicipaddress.ip), 'routeros', networkid, publicgwip=publicgw, publiccidr=publiccidr)
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
        cloudspaceId = int(cloudspaceId)
        #A cloudspace may not contain any resources any more
        query = {'cloudspaceId': cloudspaceId, 'status': {'$ne': 'DESTROYED'}}
        results = self.models.vmachine.search(query)[1:]
        if len(results) > 0:
            ctx.start_response('409 Conflict', [])
            return 'In order to delete a CloudSpace it can not contain Machine Buckets.'
        #The last cloudspace in a space may not be deleted
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        query  = {'accountId': cloudspace.accountId,
                  'status': {'$ne': 'DESTROYED'},
                  'id': {'$ne': cloudspaceId}}
        results = self.models.cloudspace.search(query)[1:]
        if len(results) == 0:
            ctx.start_response('409 Conflict', [])
            return 'The last CloudSpace of an account can not be deleted.'

        cloudspace.status = "DESTROYING"
        self.models.cloudspace.set(cloudspace)
        cloudspace = self._release_resources(cloudspace)
        cloudspace.status = 'DESTROYED'
        cloudspace.deletionTime = int(time.time())
        self.models.cloudspace.set(cloudspace)


    @authenticator.auth(acl='R')
    @audit()
    def get(self, cloudspaceId, **kwargs):
        """
        get cloudspaces.
        param:cloudspaceId id of the cloudspace
        result dict
        """
        cloudspaceObject = self.models.cloudspace.get(int(cloudspaceId))

        #For backwards compatibility, set the secret if it is not filled in
        if len(cloudspaceObject.secret) == 0:
            cloudspaceObject.secret = str(uuid.uuid4())
            self.models.cloudspace.set(cloudspaceObject)

        cloudspace_acl = authenticator.auth([]).getCloudspaceAcl(cloudspaceObject.id)
        cloudspace = { "accountId": cloudspaceObject.accountId,
                        "acl": [{"right": ace.right, "type": ace.type, "userGroupId": ace.userGroupId} for _, ace in cloudspace_acl.iteritems()],
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
        cloudspace = self.models.cloudspace.get(int(cloudspaceId))
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
        query = {'status': {'$ne': 'DISABLED'}}
        nondisabledaccounts = self.models.account.search(query)[1:]
        nondisabled = [account['id'] for account in nondisabledaccounts]
        cloudspaceaccess = set()

        # get cloudspaces access via account
        q = {'acl.userGroupId': user, 'status': {'$ne': 'DISABLED'}}
        query = {'$query': q, '$fields': ['id']}
        accountaccess = set(ac['id'] for ac in self.models.account.search(query)[1:])
        q = {'accountId': {'$in': list(accountaccess)}}
        query = {'$query': q, '$fields': ['id']}
        cloudspaceaccess.update(cs['id'] for cs in self.models.cloudspace.search(query)[1:])

        # get cloudspaces access via atleast one vm
        q = {'acl.userGroupId': user, 'status': {'$ne': 'DESTROYED'}}
        query = {'$query': q, '$fields': ['cloudspaceId']}
        cloudspaceaccess.update(vm['cloudspaceId'] for vm in self.models.vmachine.search(query)[1:])

        fields = ['id', 'name', 'descr', 'status', 'accountId','acl','publicipaddress','location']
        q = {"accountId": {"$in": nondisabled}, 
             "$or": [{"acl.userGroupId": user}, 
                     {"id": {"$in": list(cloudspaceaccess)} }],
             "status": {"$ne": "DESTROYED"}}
        query = {'$query': q, '$fields': fields}
        cloudspaces = self.models.cloudspace.search(query)[1:]

        for cloudspace in cloudspaces:
            account = self.models.account.get(cloudspace['accountId'])
            cloudspace['publicipaddress'] = getIP(cloudspace['publicipaddress'])
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
        Get information about the defense shield
        param:cloudspaceId id of the cloudspace
        """
        ctx = kwargs['ctx']
        cloudspaceId = int(cloudspaceId)
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceId)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'

        fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
        pwd = str(uuid.uuid4())
        self.netmgr.fw_set_password(fwid, 'admin', pwd)
        location = self.hrd.get('mothership1.cloudbroker.defense_proxy')                    


        url = 'https://%s.defense.%s/webfig' % ('-'.join(getIP(cloudspace.publicipaddress).split('.')),location)
        result = {'user': 'admin', 'password': pwd, 'url': url}
        return result
