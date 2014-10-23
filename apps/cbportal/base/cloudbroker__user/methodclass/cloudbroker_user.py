from JumpScale import j
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import md5

class cloudbroker_user(j.code.classGetBase()):
    """
    Operator actions for interventions specific to a user
    """
    def __init__(self):
        
        self._te = {}
        self.actorname = "user"
        self.appname = "cloudbroker"
        self._cb = None
        self.syscl = j.core.osis.getClientForNamespace('system')
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.users_actor = self.cb.extensions.imp.actors.cloudapi.users

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    def _checkUser(self, username):
        users = self.syscl.user.search({'id': username})[1:]
        if not users:
            return False, 'User %s does not exist' % username
        return True, users[0]

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

    @auth(['level1', 'level2'])
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

    @auth(['level1', 'level2'])
    def sendResetPasswordLink(self, username, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        check, result = self._checkUser(username)
        if not check:
            ctx.start_response('404', headers)
            return result
        email = result['emails']
        return self.users_actor.sendResetPasswordLink(email)

    @auth(['level1', 'level2'])
    def delete(self, username, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        check, result = self._checkUser(username)
        if not check:
            ctx.start_response('404', headers)
            return result
        user = result
        
        #delete all acls
        #delete from accounts
        query = {'acl.userGroupId': 'reem', 'acl.type':'U'}
        accountswiththisuser = self.cbcl.account.search(query)[1:]
        for account in accountswiththisuser:
            rights = {acl['userGroupId']: acl['right'] for acl in account['acl']}
            admins = ['A' for right in rights.values() if 'A' in right]
            if 'A' in rights[username] and len(admins) < 2 and not account['name']==username:
                ctx.start_response('403', headers)
                return 'Cannot delete last Admin user of an account'
            account['acl'] = [acl for acl in account['acl'] if username not in acl['userGroupId']]
            self.cbcl.account.set(account)

        #delete from cloudspaces
        cloudspaceswiththisuser = self.cbcl.cloudspace.search(query)[1:]
        for cloudspace in cloudspaceswiththisuser:
            cloudspace['acl'] = [acl for acl in cloudspace['acl'] if username not in acl['userGroupId']]
            self.cbcl.cloudspace.set(cloudspace)

        user['active'] = False
        self.syscl.user.set(user)
        return True