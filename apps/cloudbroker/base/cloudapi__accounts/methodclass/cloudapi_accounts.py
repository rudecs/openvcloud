from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor
from JumpScale.portal.portal import exceptions

class cloudapi_accounts(BaseActor):
    """
    API Actor api for managing account

    """
    def __init__(self):
        super(cloudapi_accounts, self).__init__()
        self.systemodel = j.clients.osis.getNamespace('system')

    @authenticator.auth(acl={'account': set('U')})
    @audit()
    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights

        :param accountId: id of the account
        :param userId: username or emailaddress of the user to grant access
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user was added successfully
        """
        user = self.cb.checkUser(userId, activeonly=False)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with ID
            userId = user['id']

        self._addACE(accountId, userId, accesstype, userstatus='CONFIRMED')
        emailaddress = user['emails'][0]
        try:
            j.apps.cloudapi.users.sendShareResourceEmail(emailaddress, 'account', accountId,
                                                         accesstype,  userId, user['active'])
            return True
        except:
            self.deleteUser(accountId, userId, recursivedelete=False)
            raise

    @authenticator.auth(acl={'account': set('U')})
    @audit()
    def addExternalUser(self, accountId, emailaddress, accesstype, **kwargs):
        """
        Give an unregistered user access rights by sending an invite email

        :param accountId: id of the account
        :param emailaddress: emailaddress of the unregistered user that will be invited
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user was added successfully
        """
        if self.systemodel.user.search({'emails': emailaddress})[1:]:
            raise exceptions.BadRequest('User is already registered on the system, please add as '
                                        'a normal user')

        self._addACE(accountId, emailaddress, accesstype, userstatus='INVITED')
        try:
            j.apps.cloudapi.users.sendInviteLink(emailaddress, 'account', accountId, accesstype)
            return True
        except:
            self.deleteUser(accountId, emailaddress, recursivedelete=False)
            raise

    def _addACE(self, accountId, userId, accesstype, userstatus='CONFIRMED'):
        """
        Add a new ACE to the ACL of the account

        :param accountId: id of the account
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was added successfully
        """
        accountId = int(accountId)
        if not self.models.account.exists(accountId):
            raise exceptions.NotFound('Account does not exist')

        self.cb.isValidRole(accesstype)
        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                raise exceptions.BadRequest('User already has access rights to this account')

        acl = account.new_acl()
        acl.userGroupId = userId
        acl.type = 'U'
        acl.right = accesstype
        acl.status = userstatus
        self.models.account.set(account)
        return True

    @authenticator.auth(acl={'account': set('U')})
    @audit()
    def updateUser(self, accountId, userId, accesstype, **kwargs):
        """
        Update user access rights

        :param accountId: id of the account
        :param userId: userid/email for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        :return True if user access was updated successfully
        """
        accountId = int(accountId)
        if not self.models.account.exists(accountId):
            raise exceptions.NotFound('Account does not exist')

        self.cb.isValidRole(accesstype)
        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                if self.cb.isaccountuserdeletable(ace, account.acl):
                    ace.right = accesstype
                else:
                    raise exceptions.BadRequest('User is last admin on the account, cannot change '
                                                'user\'s access rights')
                break
        else:
            raise exceptions.NotFound('User does not have any access rights to update')

        self.models.account.set(account)
        return True

    @audit()
    def create(self, name, access, maxMemoryCapacity=None, maxVDiskCapacity=None,
               maxCPUCapacity=None, maxNASCapacity=None, maxArchiveCapacity=None,
               maxNetworkOptTransfer=None, maxNetworkPeerTransfer=None, maxNumPublicIP=None,
               **kwargs):
        """
        Create a extra an account (Method not implemented)

        :param name: name of account to create
        :param access: list of ids of users which have full access to this account
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNASCapacity: max size of primary(NAS) storage in TB
        :param maxArchiveCapacity: max size of secondary(Archive) storage in TB
        :param maxNetworkOptTransfer: max sent/received network transfer in operator
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return int
        """
        raise NotImplementedError("Not implemented method create")

    @authenticator.auth(acl={'account': set('D')})
    @audit()
    def delete(self, accountId, **kwargs):
        """
        Delete an account (Method not implemented)

        :param accountId: id of the account
        :return bool True if deletion was successful
        """
        raise NotImplementedError("Not implemented method delete")

    @authenticator.auth(acl={'account': set('R')})
    @audit()
    def get(self, accountId, **kwargs):
        """
        Get account details

        :param accountId: id of the account
        :return dict with the account details
        """
        account = self.models.account.get(int(accountId)).dump()

        # Filter the acl (after removing the selected user) to only have admins
        admins = filter(lambda a: set(a['right']) == set('ARCXDU'), account['acl'])
        # Set canBeDeleted to True except for the last admin on the account (if more than 1 admin
        # on account then all can be deleted)
        for ace in account['acl']:
            if len(admins) <= 1 and ace in admins:
                ace['canBeDeleted'] = False
            else:
                ace['canBeDeleted'] = True
        return account

    @authenticator.auth(acl={'account': set('R')})
    @audit()
    def listTemplates(self, accountId, **kwargs):
        """
        List templates which can be managed by this account

        :param accountId: id of the account
        :return dict with the template images for the given account
        """
        fields = ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        q = {'accountId': int(accountId)}
        query = {'$query': q, '$fields': fields}
        results = self.models.image.search(query)[1:]
        return results

    @authenticator.auth(acl={'account': set('U')})
    @audit()
    def deleteUser(self, accountId, userId, recursivedelete=False, **kwargs):
        """
        Revoke user access from the account

        :param acountId: id of the account
        :param userId: id or emailaddress of the user to remove
        :param recursivedelete: recursively revoke access permissions from owned cloudspaces
                                and machines
        :return True if user access was revoked from account
        """
        accountId = int(accountId)
        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                if self.cb.isaccountuserdeletable(ace, account.acl):
                    account.acl.remove(ace)
                    self.models.account.set(account)
                else:
                    raise exceptions.BadRequest("User '%s' is the last admin on the account '%s'" %
                                                (userId, account.name))
                break
        else:
            raise exceptions.NotFound('User "%s" does not have access on the account' % userId)

        if recursivedelete:
            # Delete user accessrights from owned cloudspaces
            for cloudspace in self.models.cloudspace.search({'accountId': accountId})[1:]:
                cloudspaceupdate = False
                cloudspaceobj = self.models.cloudspace.get(cloudspace['id'])
                for ace in cloudspaceobj.acl:
                    if ace.userGroupId == userId:
                        cloudspaceobj.acl.remove(ace)
                        cloudspaceupdate = True
                if cloudspaceupdate:
                    self.models.cloudspace.set(cloudspaceobj)

                # Delete user accessrights from related machines (part of owned cloudspaces)
                for vmachine in self.models.vmachine.search({'cloudspaceId': cloudspaceobj.id})[1:]:
                    vmachineupdate = False
                    vmachineobj = self.models.vmachine.get(vmachine['id'])
                    for ace in vmachineobj.acl:
                        if ace.userGroupId == userId:
                            vmachineobj.acl.remove(ace)
                            vmachineupdate = True
                    if vmachineupdate:
                        self.models.vmachine.set(vmachineobj)

        return True

    @audit()
    def list(self, **kwargs):
        """
        List all accounts the user has access to

        :return list with every element containing details of a account as a dict
        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        fields = ['id', 'name', 'acl']
        q = {'acl.userGroupId': user}
        query = {'$query': q, '$fields': fields}
        accounts = self.models.account.search(query)[1:]
        return accounts

    @authenticator.auth(acl={'account': set('A')})
    @audit()
    def update(self, accountId, name=None, maxMemoryCapacity=None, maxVDiskCapacity=None,
               maxCPUCapacity=None, maxNASCapacity=None, maxArchiveCapacity=None,
               maxNetworkOptTransfer=None, maxNetworkPeerTransfer=None, maxNumPublicIP=None, **kwargs):
        """
        Update an account name or the maximum cloud units set on it
        Setting a cloud unit maximum to -1 will not put any restrictions on the resource

        :param accountId: id of the account to change
        :param name: name of the account
        :param maxMemoryCapacity: max size of memory in GB
        :param maxVDiskCapacity: max size of aggregated vdisks in GB
        :param maxCPUCapacity: max number of cpu cores
        :param maxNASCapacity: max size of primary(NAS) storage in TB
        :param maxArchiveCapacity: max size of secondary(Archive) storage in TB
        :param maxNetworkOptTransfer: max sent/received network transfer in operator
        :param maxNetworkPeerTransfer: max sent/received network transfer peering
        :param maxNumPublicIP: max number of assigned public IPs
        :return: True if update was successful
        """

        accountobj = self.models.account.get(accountId)

        if name:
            accountobj.name = name

        if maxMemoryCapacity is not None:
            consumedmemcapacity = self.getConsumedCloudUnitsByType(accountId, 'CU_M')
            if maxMemoryCapacity != -1 and maxMemoryCapacity < consumedmemcapacity:
                raise exceptions.BadRequest("Cannot set the maximum memory capacity to a value "
                                            "that is less than the current consumed memory "
                                            "capacity %s GB." % consumedmemcapacity)
            else:
                accountobj.resourceLimits['CU_M'] = maxMemoryCapacity

        if maxVDiskCapacity is not None:
            consumedvdiskcapacity = self.getConsumedCloudUnitsByType(accountId, 'CU_D')
            if maxVDiskCapacity != -1 and maxVDiskCapacity < consumedvdiskcapacity:
                raise exceptions.BadRequest("Cannot set the maximum vdisk capacity to a value that "
                                            "is less than the current consumed vdisk capacity %s "
                                            "GB." % consumedvdiskcapacity)
            else:
                accountobj.resourceLimits['CU_D'] = maxVDiskCapacity

        if maxCPUCapacity is not None:
            consumedcpucapacity = self.getConsumedCloudUnitsByType(accountId, 'CU_C')
            if maxCPUCapacity != -1 and maxCPUCapacity < consumedcpucapacity:
                raise exceptions.BadRequest("Cannot set the maximum cpu cores to a value that "
                                            "is less than the current consumed cores %s "
                                            "GB." % consumedcpucapacity)
            else:
                accountobj.resourceLimits['CU_C'] = maxCPUCapacity

        if maxNASCapacity is not None:
            consumednascapacity = self.getConsumedCloudUnitsByType(accountId, 'CU_S')
            if maxNASCapacity != -1 and maxNASCapacity < consumednascapacity:
                raise exceptions.BadRequest("Cannot set the maximum primary storage capacity to a "
                                            "value that is less than the current consumed capacity "
                                            "%s TB." % consumednascapacity)
            else:
                accountobj.resourceLimits['CU_S'] = maxNASCapacity

        if maxArchiveCapacity is not None:
            consumedarchivecapacity = self.getConsumedCloudUnitsByType(accountId, 'CU_A')
            if maxArchiveCapacity != -1 and maxArchiveCapacity < consumedarchivecapacity:
                raise exceptions.BadRequest("Cannot set the maximum secondary storage capacity to "
                                            "a value that is less than the current consumed "
                                            "capacity %s TB." % consumedarchivecapacity)
            else:
                accountobj.resourceLimits['CU_A'] = maxArchiveCapacity

        if maxNetworkOptTransfer is not None:
            transferednewtopt = self.getConsumedCloudUnitsByType(accountId, 'CU_NO')
            if maxNetworkOptTransfer != -1 and maxNetworkOptTransfer < transferednewtopt:
                raise exceptions.BadRequest("Cannot set the maximum network transfer in operator "
                                            "to a value that is less than the current  "
                                            "sent/received %s GB." % transferednewtopt)
            else:
                accountobj.resourceLimits['CU_NO'] = maxNetworkOptTransfer

        if maxNetworkPeerTransfer is not None:
            transferednewtpeer = self.getConsumedCloudUnitsByType(accountId, 'CU_NP')
            if maxNetworkPeerTransfer != -1 and maxNetworkPeerTransfer < transferednewtpeer:
                raise exceptions.BadRequest("Cannot set the maximum network transfer peering "
                                            "to a value that is less than the current  "
                                            "sent/received %s GB." % transferednewtpeer)
            else:
                accountobj.resourceLimits['CU_NP'] = maxNetworkPeerTransfer

        if maxNumPublicIP is not None:
            assingedpublicip = self.getConsumedCloudUnitsByType(accountId, 'CU_I')
            if maxNumPublicIP != -1 and maxNumPublicIP < assingedpublicip:
                raise exceptions.BadRequest("Cannot set the maximum number of public IPs "
                                            "to a value that is less than the current  "
                                            "assigned %s." % assingedpublicip)
            else:
                accountobj.resourceLimits['CU_I'] = maxNumPublicIP

        self.models.account.set(accountobj)
        return True

    @authenticator.auth(acl={'account': set('R')})
    @audit()
    def getCreditBalance(self, accountId, **kwargs):
        """
        Get the current available credit balance

        :param accountId: id of the account
        :return json dict containing the available credit
        """
        # For now, don't get the balance statement, just calculate it
        #query = {'fields': ['time', 'credit']}
        #query['query'] = {'term': {"accountId": accountId}}
        #query['size'] = 1
        #query['sort'] = [{ "time" : {'order':'desc', 'ignore_unmapped' : True}}]
        #results = self.models.creditbalance.find(ujson.dumps(query))['result']
        #balance = [res['fields'] for res in results]

        #return balance[0] if len(balance) > 0 else {'credit':0, 'time':-1}

        fields = ['time', 'credit', 'status']
        q = {'accountId': int(accountId), 'status': {'$ne': 'UNCONFIRMED'}}
        query = {'$query': q, '$fields': fields}
        history = self.models.credittransaction.search(query)[1:]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
        import time
        return {'credit': balance, 'time': int(time.time())}

    @authenticator.auth(acl={'account': set('R')})
    @audit()
    def getCreditHistory(self, accountId, **kwargs):
        """
        Get all the credit transactions (positive and negative) for this account

        :param accountId: id of the account
        :return list with the transactions details each as a dict
        """

        fields = ['time', 'currency', 'amount', 'credit','reference', 'status', 'comment']
        q = {"accountId": int(accountId)}
        query = {'$query': q, '$fields': fields}
        history = self.models.credittransaction.search(query)[1:]
        return history

    @authenticator.auth(acl={'account': set('R')})
    def getConsumedCloudUnits(self, accountId, **kwargs):
        """
        Calculate the currently consumed cloud units for all cloudspaces in the account.

        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of virtual cpu cores
        - CU_D: consumed virtual disk storage in GB
        - CU_S: consumed primary storage (NAS) in TB
        - CU_A: consumed secondary storage (Archive) in TB
        - CU_NO: sent/received network transfer in operator in GB
        - CU_NP: sent/received network transfer peering in GB
        - CU_I: number of public IPs

        :param accountId: id of the account consumption should be calculated for
        :return: dict with the consumed cloud units
        """
        consumedcudict = {'CU_M': 0, 'CU_C': 0, 'CU_D': 0, 'CU_I': 0}
        # The following keys are unimplemented cloud unit consumptions, will set to 0 until
        # consumption is properly calculated
        unimplementedcu = {'CU_S': 0, 'CU_A': 0, 'CU_NO': 0, 'CU_NP': 0}

        # Aggregate the total consumed cloud units for all cloudspaces in the account
        for cloudspace in self.models.cloudspace.search({'accountId': accountId,
                                                         'status': 'DEPLOYED'})[1:]:
            cloudspaceconsumption = j.apps.cloudapi.cloudspaces.getConsumedCloudUnits(
                 cloudspace['id'])
            for cu in consumedcudict:
                consumedcudict[cu] += cloudspaceconsumption[cu]

        consumedcudict.update(unimplementedcu)
        return consumedcudict

    @authenticator.auth(acl={'account': set('R')})
    def getConsumedCloudUnitsByType(self, accountId, cutype, **kwargs):
        """
        Calculate the currently consumed cloud units of the specified type for all cloudspaces
        in the account.

        Possible types of cloud units are include:
        - CU_M: returns consumed memory in GB
        - CU_C: returns number of virtual cpu cores
        - CU_D: returns consumed virtual disk storage in GB
        - CU_S: returns consumed primary storage (NAS) in TB
        - CU_A: returns consumed secondary storage (Archive) in TB
        - CU_NO: returns sent/received network transfer in operator in GB
        - CU_NP: returns sent/received network transfer peering in GB
        - CU_I: returns number of public IPs

        :param accountId: id of the account consumption should be calculated for
        :param cutype: cloud unit resource type
        :return: float/int for the consumed cloud unit of the specified type
        """
        consumedcutype = 0

        # For the following cloud unit types 'CU_S', 'CU_A', 'CU_NO', 'CU_NP', 0 will be returned
        # until proper consumption calculation is implemented
        if cutype == 'CU_M':
            cumethod = j.apps.cloudapi.cloudspaces.getConsumedMemoryCapacity
        elif cutype == 'CU_C':
            cumethod = j.apps.cloudapi.cloudspaces.getConsumedCPUCores
        elif cutype == 'CU_D':
            cumethod = j.apps.cloudapi.cloudspaces.getConsumedVDiskCapacity
        elif cutype == 'CU_S':
            return 0
        elif cutype == 'CU_A':
            return 0
        elif cutype == 'CU_NO':
            return 0
        elif cutype == 'CU_NP':
            return 0
        elif cutype == 'CU_I':
            cumethod = j.apps.cloudapi.cloudspaces.getConsumedPublicIPs
        else:
            raise exceptions.BadRequest('Invalid cloud unit type: %s' % cutype)

        for cloudspace in self.models.cloudspace.search({'accountId': accountId,
                                                         'status': 'DEPLOYED'})[1:]:
            consumedcutype += cumethod(cloudspace['id'])

        return consumedcutype
