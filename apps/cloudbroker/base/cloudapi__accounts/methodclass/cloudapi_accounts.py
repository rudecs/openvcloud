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
        user = self.cb.checkUser(userId)
        if not user:
            raise exceptions.NotFound("User is not registered on the system")
        else:
            # Replace email address with ID
            userId = user['id']

        return self._addACE(accountId, userId, accesstype, userstatus='CONFIRMED')

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

        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.userGroupId == userId:
                raise exceptions.BadRequest('User already has access rights to account')

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

        account = self.models.account.get(accountId)
        isadminuser = False
        for ace in account.acl:
            if ace.userGroupId == userId:
                if ace.right == 'ARCXDU':
                    isadminuser = True
                ace.right = accesstype
                break
        else:
            raise exceptions.NotFound('User does not have any access rights to update')

        if isadminuser:
            # Filter the acl (after removing the selected user) to only have admins
            otheradmins = filter(lambda a: set(a.right) == set('ARCXDU'), account.acl)
            if not otheradmins:
                raise exceptions.BadRequest('User is last admin on the account, cannot change '
                                            'user\'s access rights')

        self.models.account.set(account)
        return True

    @audit()
    def create(self, name, access, **kwargs):
        """
        Create a extra an account (Method not implemented)

        :param name: name of account to create
        :param access: list of ids of users which have full access to this account
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
        # User with selected username has admin rights on account
        isadminuser = False
        update = False
        for ace in account.acl:
            if ace.userGroupId == userId:
                account.acl.remove(ace)
                update = True
                if ace.right == 'ARCXDU':
                    isadminuser = True

        if not update:
            raise exceptions.NotFound('User "%s" does not have access on the account' % userId)
        elif isadminuser:
            # Filter the acl (after removing the selected user) to only have admins
            otheradmins = filter(lambda a: set(a.right) == set('ARCXDU'), account.acl)
            if not otheradmins:
                raise exceptions.BadRequest('User "%s" is last admin on the account' % userId)
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
    def update(self, accountId, name, **kwargs):
        """
        Update an account name (Method not implemented)

        :param accountId: id of the account to change
        :param name: name of the account
        :return int id of account updated
        """
        raise NotImplementedError("Not implemented method update")

    @authenticator.auth(acl={'account': set('A')})
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
