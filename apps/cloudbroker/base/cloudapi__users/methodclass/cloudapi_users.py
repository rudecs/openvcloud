from JumpScale import j
from cloudapi_users_osis import cloudapi_users_osis


class cloudapi_users(cloudapi_users_osis):

    """
    User management

    """

    def __init__(self):

        self._te = {}
        self.actorname = "users"
        self.appname = "cloudapi"
        cloudapi_users_osis.__init__(self)
        self._cb = None

        pass


    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb
    
    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel('system', 'usermanager')
        return self._models

    def authenticate(self, username, password, **kwargs):
        """
        The function evaluates the provided username and password and returns a session key.
        The session key can be used for doing api requests. E.g this is the authkey parameter in every actor request.
        A session key is only vallid for a limited time.
        param:username username to validate
        param:password password to validate
        result str,,session
        """
        ctx = kwargs['ctx']
        if j.apps.system.usermanager.authenticate(username, password):
            session = ctx.env['beaker.get_session']() #create new session
            session['user'] = username
            session.save()
            return session.id
        else:
            ctx.start_response('401 Unauthorized', [])
            return

    def register(self, username, emailaddress, password, **kwargs):
        """
        Register a new user, a user is registered with a login, password and a new account is created.
        param:username unique username for the account
        param:emailaddress unique emailaddress for the account
        param:password unique password for the account
        result bool 
        
        """
        ctx = kwargs['ctx']
        if j.apps.system.usermanager.userexists(username):
            ctx.start_response('409 Conflict', [])
        else:
            j.apps.system.usermanager.usercreate(username, password,key=None, groups=username, emails=emailaddress, userid=None, reference="", remarks='', config=None)
            account = self.models.account.new()
            account.name = username
            ace = account.new_acl()
            ace.userGroupId = username
            ace.type = 'U'
            ace.right = 'CXDRAU'
            accountid = self.models.account.set(account.obj2dict())
            cs = self.models.cloudspace.new()
            cs.name = 'default'
            cs.accountId = accountid
            ace = cs.new_acl()
            ace.userGroupId = username
            ace.type = 'U'
            ace.right = 'CXDRAU'
            self.models.cloudspace.set(cs.obj2dict())
            return True







