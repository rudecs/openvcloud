from JumpScale import j
import JumpScale.grid.agentcontroller
import re, string, random, time

class cloudapi_users(object):
    """
    User management

    """
    def __init__(self):

        self._te = {}
        self.actorname = "users"
        self.appname = "cloudapi"
        self._cb = None
        self._models = None
        self.libvirt_actor = j.apps.libcloud.libvirt
        self.acl = j.clients.agentcontroller.get()


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
        accounts = self.models.account.simpleSearch({'name':username.lower()})
        if accounts and accounts[0].get('status','CONFIRMED'] != 'UNCONFIRMED':
            if j.core.portal.active.auth.authenticate(username, password):
                session = ctx.env['beaker.get_session']() #create new session
                session['user'] = username
                session.save()
                return session.id

        ctx.start_response('401 Unauthorized', [])
        return 'Unauthorized'

    def get(self, username, **kwargs):
        """
        Get information of a existing username based on username id
        param:username username of the user
        result:
        """
        user = j.core.portal.active.auth.getUserInfo(username)
        if user:
            return {'username':user.id, 'emailaddresses':user.emails}
        else:
            ctx = kwargs['ctx']
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    def _isValidUserName(self, username):
        r = re.compile('^[a-z0-9]{1,20}$')
        return r.match(username) is not None

    def _isValidPassword(self, password):
        if len(password) < 8 or len (password) > 80:
            return False
        return re.search(r"\s",password) is None

    def register(self, username, user, emailaddress, password, company, companyurl, location, **kwargs):
        """
        Register a new user, a user is registered with a login, password and a new account is created.
        param:username unique username for the account
        param:emailaddress unique emailaddress for the account
        param:password unique password for the account
        result bool
        """

        ctx = kwargs['ctx']
        if not self._isValidUserName(username):
            ctx.start_response('400 Bad Request', [])
            return '''An account name may not exceed 20 characters
             and may only contain a-z and 0-9'''
        if not self._isValidPassword(password):
            ctx.start_response('400 Bad Request', [])
            return '''A password must be at least 8 and maximum 80 characters long
                      and may not contain whitespace'''

        if j.core.portal.active.auth.userExists(username):
            ctx.start_response('409 Conflict', [])
            return 'User already exists'
        else:
            now = int(time.time())

            if not location in ('US1',):
                location = 'CA1'

            j.core.portal.active.auth.createUser(username, password, emailaddress, username, None)
            account = self.models.account.new()
            account.name = username
            account.creationTime = now
            account.DCLocation = location
            account.company = company
            account.companyurl = companyurl
            account.status = 'UNCONFIRMED'
            account.displayname = user

            ace = account.new_acl()
            ace.userGroupId = username
            ace.type = 'U'
            ace.right = 'CXDRAU'
            accountid = self.models.account.set(account)[0]


            #create activationtoken
            actual_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
            activation_token = self.models.accountactivationtoken.new()
            activation_token.id = actual_token
            activation_token.creationTime = now
            activation_token.accountId = accountid
            self.models.accountactivationtoken.set(activation_token)

            import urlparse
            urlparts = urlparse.urlsplit(ctx.env['HTTP_REFERER'])
            portalurl = '%s://%s' % (urlparts.scheme, urlparts.hostname)

            args = {'accountid': accountid, 'password': password, 'email': emailaddress, 'now': now, 'portalurl': portalurl, 'token': actual_token, 'username':username, 'user': user}
            self.acl.executeJumpScript('cloudscalers', 'cloudbroker_accountcreate', args=args, nid=j.application.whoAmI.nid, wait=False)

            return True

    def validate(self, validationtoken, **kwargs):
        if not self.models.accountactivationtoken.exists(validationtoken):
            ctx = kwargs['ctx']
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'
        activation_token = self.models.accountactivationtoken.get(validationtoken)
        accountId = activation_token.accountId
        activation_token.deletionTime = int(time.time())
        account = self.models.account.get(accountId)
        account.status = 'CONFIRMED'
        self.models.account.set(account)
        self.models.accountactivationtoken.set(activation_token)

        return True
