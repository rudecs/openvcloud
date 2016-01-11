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

    @authenticator.auth(acl='A')
    @audit()
    def addUser(self, accountId, userId, accesstype, **kwargs):
        """
        Give a registered user access rights.
        Access rights can be 'R' or 'W'
        :param:accountId id of the account
        :param:userId: id or emailaddress of the user to give access
        :param:accesstype: 'R' for read only access, 'W' for Write access
        :return True if user was was successfully added

        """
        user = self.cb.checkUser(userId)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with ID
            userId = user['id']

        return self._addACE(accountId, userId, accesstype, userstatus='CONFIRMED')

    @authenticator.auth(acl='A')
    @audit()
    def addExternalUser(self, accountId, emailaddress, accesstype, **kwargs):
        """
        Give an unregistered user access rights by sending an invite email.
        Access rights can be 'R' or 'W'
        :param:accountId id of the account
        :param:emailaddress: emailaddress of the unregistered user that will be invited
        :param:accesstype: 'R' for read only access, 'W' for Write access
        :return True if user was was successfully added
        """
        if self.systemodel.user.search({'emails': emailaddress})[1:]:
            raise exceptions.PreconditionFailed('User is already registered on the system, '
                                                'please add as a normal user')

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
        :param userId: userid for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'W' for Write access
        :param userstatus: status of the user (CONFIRMED or INVITED)
        :return True if ACE was successfully added
        """
        accountId = int(accountId)
        if not self.models.account.exists(accountId):
            raise exceptions.NotFound('Account does not exist')

        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                raise exceptions.PreconditionFailed('User already has access rights to account')

        acl = account.new_acl()
        acl.userGroupId = userId
        acl.type = 'U'
        acl.right = accesstype
        acl.status = userstatus
        self.models.account.set(account)
        return True

    @authenticator.auth(acl='U')
    @audit()
    def updateUser(self, accountId, userId, accesstype, **kwargs):
        """
        Update user access rights.
        :param: accountId id of the account
        :param userId: userid for registered users or emailaddress for unregistered users
        :param accesstype: 'R' for read only access, 'W' for Write access
        :return True if user access was successfully updated
        """
        accountId = int(accountId)
        if not self.models.account.exists(accountId):
            raise exceptions.NotFound('Account does not exist')

        # Check if user exists in the system or is an unregistered invited user
        existinguser = self.systemodel.user.search({'id': userId})[1:]
        if existinguser:
            userstatus = 'CONFIRMED'
        else:
            userstatus = 'INVITED'

        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                ace.right = accesstype
                self.models.account.set(account)
                break
        else:
            raise exceptions.PreconditionFailed('User does not have any access rights to update')

        return True

    @authenticator.auth(acl='S')
    @audit()
    def create(self, name, access, **kwargs):
        """
        Create a extra an account
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        result int
        """
        raise NotImplementedError("not implemented method create")

    @authenticator.auth(acl='S')
    @audit()
    def delete(self, accountId, **kwargs):
        """
        Delete an account
        param:accountId id of the account
        result bool,
        """
        raise NotImplementedError("not implemented method delete")

    @authenticator.auth(acl='R')
    @audit()
    def get(self, accountId, **kwargs):
        """
        get account.
        param:accountId id of the account
        result dict
        """
        #put your code here to implement this method

        return self.models.account.get(int(accountId)).dump()

    @authenticator.auth(acl='R')
    @audit()
    def listTemplates(self, accountId, **kwargs):
        """
        List templates which can be managed by this account
        param:accountId id of the account
        result dict
        """
        fields = ['id', 'name','description', 'type', 'UNCPath', 'size', 'username', 'accountId', 'status']
        q = {'accountId': int(accountId)}
        query = {'$query': q, '$fields': fields}
        results = self.models.image.search(query)[1:]
        return results

    @authenticator.auth(acl='A')
    @audit()
    def deleteUser(self, accountId, userId, recursivedelete=False, **kwargs):
        """
        Delete a user from the account
        :param acountId: id of the account
        :param userId: id of the user to remove
        :param recursivedelete: recursively delete access permissions from owned cloudspaces
                                and machines
        result
        """
        account = self.models.account.get(accountId)
        update = False
        for ace in account.acl:
            if ace.userGroupId == userId:
                account.acl.remove(ace)
                update = True
        if update:
            self.models.account.set(account)

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

        return update

    @audit()
    def list(self, **kwargs):
        """
        List accounts.
        result [],

        """
        ctx = kwargs['ctx']
        user = ctx.env['beaker.session']['user']
        fields = ['id', 'name', 'acl']
        q = {'acl.userGroupId': user}
        query = {'$query': q, '$fields': fields}
        accounts = self.models.account.search(query)[1:]
        return accounts

    @authenticator.auth(acl='A')
    @audit()
    def update(self, accountId, name, **kwargs):
        """
        Update an account name
        param:accountId id of the account to change
        param:name name of the account
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method update")

    @authenticator.auth(acl='R')
    @audit()
    def getCreditBalance(self, accountId, **kwargs):
        """
        Get the current available credit
        param:accountId id of the account
        result:dict A json dict containing the available credit
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
        return {'credit':balance, 'time':int(time.time())}

    @authenticator.auth(acl='R')
    @audit()
    def getCreditHistory(self, accountId, **kwargs):
        """
        Get all the credit transactions (positive and negative) for this account.
        param:accountId id of the account
        result:[] A json list with the transactions details.
        """

        fields = ['time', 'currency', 'amount', 'credit','reference', 'status', 'comment']
        q = {"accountId": int(accountId)}
        query = {'$query': q, '$fields': fields}
        history = self.models.credittransaction.search(query)[1:]
        return history
