from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
import JumpScale.grid.agentcontroller
import JumpScale.baselib.mailclient
import re, string, random, time
import md5

def _send_signup_mail(**kwargs):
    notifysupport = j.application.config.get("mothership1.cloudbroker.notifysupport")
    fromaddr = 'support@mothership1.com'
    toaddrs  =  [kwargs['email']]
    if notifysupport == '1':
        toaddrs.append('support@mothership1.com')


    html = """
<html>
<head></head>
<body>
    Dear %(user)s,<br>
    <br>
    Thank you for registering at Mothership<sup>1</sup>!<br>
    <br>
    We have now prepared your account %(username)s and we have applied a welcoming credit so you can start right away!<br>
    <br>
    Please confirm your e-mail address by following the activation link: <br>
    <br>
    <a href="%(portalurl)s/wiki_gcb/AccountActivation?activationtoken=%(activationtoken)s">%(portalurl)s/wiki_gcb/AccountActivation?activationtoken=%(activationtoken)s</a><br>
    <br>
    If you are unable to follow the link, please copy and paste it in your favourite browser.<br>
    <br>
    After your validation, you will be able to log in with your username and chosen password.<br>
    <br>
    Best Regards,<br>
    <br>
    The Mothership<sup>1</sup> Team<br>
    <a href="%(portalurl)s">www.mothership1.com</a><br>
</body>
</html>
""" % kwargs

    j.clients.email.send(toaddrs, fromaddr, "Mothership1 account activation", html, files=None)

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
        if accounts and accounts[0].get('status','CONFIRMED') != 'UNCONFIRMED':
            if j.core.portal.active.auth.authenticate(username, password):
                session = ctx.env['beaker.get_session']() #create new session
                session['user'] = username
                session.save()
                return session.id

        ctx.start_response('401 Unauthorized', [])
        return 'Unauthorized'

    @audit()
    def get(self, username, **kwargs):
        """
        Get information of a existing username based on username id
        param:username username of the user
        result:
        """
        ctx = kwargs['ctx']
        logedinuser = ctx.env['beaker.session']['user']
        if logedinuser != username:
            ctx.start_response('403 Forbidden', [])
            return 'Forbidden'

        user = j.core.portal.active.auth.getUserInfo(username)
        if user:
            return {'username':user.id, 'emailaddresses':user.emails}
        else:
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    def _isValidUserName(self, username):
        r = re.compile('^[a-z0-9]{1,20}$')
        return r.match(username) is not None

    def _isValidPassword(self, password):
        if len(password) < 8 or len (password) > 80:
            return False
        return re.search(r"\s",password) is None

    def updatePassword(self, oldPassword, newPassword, **kwargs):
        """
        Change user password
        result:
        """
        ctx = kwargs['ctx']
        user = j.core.portal.active.auth.getUserInfo(ctx.env['beaker.session']['user'])
        if user:
              if user.passwd == md5.new(oldPassword).hexdigest():
                 if not self._isValidPassword(newPassword):
                    return [400, "A password must be at least 8 and maximum 80 characters long and may not contain whitespace."]
                 else:
                    cl = j.core.osis.getClient(user='root')
                    usercl = j.core.osis.getClientForCategory(cl, 'system', 'user')
                    user.passwd =  md5.new(newPassword).hexdigest()
                    usercl.set(user)
                    return [200, "Your password has been changed."]
              else:
                 return [400, "Your current password doesn't match."]
        else:
            ctx = kwargs['ctx']
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    def register(self, username, user, emailaddress, password, company, companyurl, location, promocode, **kwargs):
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
            return 'Username already exists'
        
        cl = j.core.osis.getClientForNamespace('system')
        #Elastic search analyzed this field, TODO: fix this
        firstemailaddresspart = emailaddress.lower().split('@')[0]
        matchingusers = cl.user.simpleSearch({'emails':firstemailaddresspart})
        existingusers = [user for user in matchingusers if user['emails'].lower() == emailaddress.lower()]
        
        if len(existingusers > 0):
            ctx.start_response('409 Conflict', [])
            return 'An account with this email address already exists'

        now = int(time.time())

        location = location.lower()

        if not location in self.cb.extensions.imp.getLocations():
            location = self.cb.extensions.imp.whereAmI()

        locationurl = self.cb.extensions.imp.getLocations()[location]
        if location != self.cb.extensions.imp.whereAmI():
            correctlocation = "%s/restmachine/cloudapi/users/register" % (locationurl)
            ctx.start_response('451 Redirect', [('Location', correctlocation)])
            return 'The request has been made on the wrong location, it should be done where the cloudspace needs to be created, in this case %s' % correctlocation

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

        signupcredit = j.application.config.getFloat('mothership1.cloudbroker.signupcredit')
        creditcomment = 'Getting you started'
        if signupcredit > 0.0:
            credittransaction = self.models.credittransaction.new()
            credittransaction.accountId = accountid
            credittransaction.amount = signupcredit
            credittransaction.credit = signupcredit
            credittransaction.currency = 'USD'
            credittransaction.comment = creditcomment
            credittransaction.status = 'CREDIT'
            credittransaction.time = now

            self.models.credittransaction.set(credittransaction)

        #create activationtoken
        actual_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        activation_token = self.models.accountactivationtoken.new()
        activation_token.id = actual_token
        activation_token.creationTime = now
        activation_token.accountId = accountid
        self.models.accountactivationtoken.set(activation_token)

        j.apps.cloudapi.cloudspaces.create(accountid, 'default', username, None, None)
        _send_signup_mail(username=username, user=user, email=emailaddress, portalurl=locationurl, activationtoken=actual_token)

        return True

    def validate(self, validationtoken, **kwargs):
        ctx = kwargs['ctx']
        now = int(time.time())
        if not self.models.accountactivationtoken.exists(validationtoken):
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        activation_token = self.models.accountactivationtoken.get(validationtoken)

        if activation_token.deletionTime > 0:
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        accountId = activation_token.accountId
        activation_token.deletionTime = now
        account = self.models.account.get(accountId)
        account.status = 'CONFIRMED'
        self.models.account.set(account)
        self.models.accountactivationtoken.set(activation_token)

        return True
