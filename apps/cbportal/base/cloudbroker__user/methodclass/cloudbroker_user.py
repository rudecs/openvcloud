from JumpScale import j
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor, wrap_remote
from JumpScale.portal.portal import exceptions
from JumpScale.baselib.http_client.HttpClient import HTTPError
import md5


class cloudbroker_user(BaseActor):
    """
    Operator actions for interventions specific to a user
    """
    def __init__(self):
        super(cloudbroker_user, self).__init__()
        self.syscl = j.clients.osis.getNamespace('system')
        self.users_actor = self.cb.actors.cloudapi.users

    def generateAuthorizationKey(self, username, **kwargs):
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        param:username name of the user an authorization key is required for
        """
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        check, result = self._checkUser(username)
        if not check:
            ctx.start_response('404', headers)
            return result
        return self.users_actor.authenticate(username, result['passwd'])

    @auth(['level1', 'level2', 'level3'])
    def updatePassword(self, username, password, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        check, result = self._checkUser(username)
        if not check:
            ctx.start_response('404', headers)
            return result
        result['passwd'] = md5.new(password).hexdigest()
        self.syscl.user.set(result)
        return True
    
    @auth(['level1', 'level2', 'level3'])
    def create(self, username, emailaddress, password, groups, **kwargs):
        groups = groups or []
        created = j.core.portal.active.auth.createUser(username, password, emailaddress, groups,
                                                       None)
        if created:
            primaryemailaddress = emailaddress[0]
            self.cb.updateResourceInvitations(username, primaryemailaddress)

        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def sendResetPasswordLink(self, username, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        check, result = self._checkUser(username)
        if not check:
            ctx.start_response('404', headers)
            return result
        email = result['emails']
        return self.users_actor.sendResetPasswordLink(email)

    @auth(['level1', 'level2', 'level3'])
    def delete(self, username, **kwargs):
        """
        Delete the user from all ACLs and set user status to inactive

        :param username: username of the user to delete
        :return: True if deletion was successful
        """
        users = self.syscl.user.search({'id': username})[1:]
        if not users:
            raise exceptions.NotFound('User does not exist.')
        else:
            userobj = self.syscl.user.get(users[0]['id'])

        query = {'acl.userGroupId': username, 'acl.type': 'U'}
        # Delete user from all accounts, if account status is Destoryed then delete without
        # further validation
        accountswiththisuser = self.models.account.search(query)[1:]
        for account in accountswiththisuser:
            if account['status'] == 'DESTROYED':
                # Delete immediately without further checks
                accountobj = self.models.account.get(account['guid'])
                accountobj.acl = filter(lambda a: a.userGroupId != username, accountobj.acl)
                self.models.account.set(accountobj)
            else:
                try:
                    self.cb.actors.cloudbroker.account.deleteUser(account['id'], username,
                                                                  recursivedelete=True)
                except HTTPError as ex:
                    if ex.status_code == 400 and ex.msg.count('is the last admin on the account'):
                        raise exceptions.BadRequest(ex.msg)
                    else:
                        raise

        # Delete user from cloudspaces
        cloudspaceswiththisuser = self.models.cloudspace.search(query)[1:]
        for cloudspace in cloudspaceswiththisuser:
            self.cb.actors.cloudbroker.cloudspace.deleteUser(cloudspace['id'], username,
                                                             recursivedelete=True)
        # Delete user from vmachines
        machineswiththisuser = self.models.vmachine.search(query)[1:]
        for machine in machineswiththisuser:
            self.cb.actors.cloudbroker.machine.deleteUser(machine['id'], username)

        # Set the user to inactive
        userobj.active = False
        self.syscl.user.set(userobj)

        return True

    @auth(['level1', 'level2', 'level3'])
    def deleteByGuid(self, userguid, **kwargs):
        """
        Delete the user from all ACLs and set user status to inactive
        Note: This actor can also be called using username instead of guid to workaround CBGrid
        allowing userguid or username

        :param userguid: guid of the user to delete
        :return: True if deletion was successful
        """
        if userguid.count("_"):
            users = self.syscl.user.search({'guid': userguid})[1:]
            username = users[0]['id']
        else:
            username = userguid
        return self.delete(username)