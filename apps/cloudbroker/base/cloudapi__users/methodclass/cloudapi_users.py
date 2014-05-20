from JumpScale import j
import JumpScale.baselib.mailclient
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
        if j.core.portal.active.auth.authenticate(username, password):
            session = ctx.env['beaker.get_session']() #create new session
            session['user'] = username
            session.save()
            return session.id
        else:
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

    def _send_signup_mail(self, **kwargs):
        shouldsendmail = j.application.config.get("mothership1.cloudbroker.sendmail")
        if shouldsendmail is not '1':
            return

        fromaddr = 'support@mothership1.com'
        toaddrs  = kwargs['emailaddress']


        html = """
<html>
    <head></head>
    <body>
        Dear %s,<br>
        <br>
        Thank you for registering %s at Mothership<sup>1</sup>!<br>
        <br>
        Please confirm your e-mail address by following the activation link: <a href="%s/AccountActivation?activationtoken=%s">%s/AccountActivation?activationtoken=%s</a><br>
        If you are unable to follow the link, please copy and paste it in your favourite browser.
        <br>
        After your validation, you will be able to log in with your username and chosen password.<br>
        <br>
        Best Regards,<br>
        <br>
        The Mothership<sup>1</sup> Team<br>
        <a href="%s">www.mothership1.com</a><br>
    </body>
</html>
""" % (kwargs['user'], kwargs['username'] , kwargs['portalurl'], kwargs['activationtoken'],kwargs['portalurl'], kwargs['activationtoken'], kwargs['portalurl'])

        j.clients.mail.send(fromaddr, toaddrs, html, "Mothership1 account activation", files=None)

    def _isValidUserName(self, username):
        r = re.compile('^[a-z0-9]{1,20}$')
        return r.match(username) is not None


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

            ace = account.new_acl()
            ace.userGroupId = username
            ace.type = 'U'
            ace.right = 'CXDRAU'
            accountid = self.models.account.set(account)[0]

            #Create CloudSpace
            networkid = self.libvirt_actor.getFreeNetworkId()
            publicipaddress = self.cb.extensions.imp.getPublicIpAddress(networkid)
            cs = self.models.cloudspace.new()
            cs.name = 'default'
            cs.accountId = accountid
            cs.networkId = networkid
            cs.publicipaddress = publicipaddress
            ace = cs.new_acl()
            ace.userGroupId = username
            ace.type = 'U'
            ace.right = 'CXDRAU'
            self.models.cloudspace.set(cs)

            #TODO: create vfw

            #create activationtoken
            actual_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
            activation_token = self.models.activationtoken.new()
            activation_token.id = actual.token()
            activation_token.creationTime = now
            self.models.activationtoken.set(activation_token)

            #Send email to verify the email address
            import urlparse
            urlparts = urlparse.urlsplit(ctx.env['HTTP_REFERER'])
            portalurl = '%s://%s' % (urlparts.scheme, urlparts.hostname)

            self._send_signup_mail(username=username, user=user, emailaddress=emailaddress, portalurl=portalurl, activationtoken=actual_token)

            return True

    def validate(self, validationtoken, **kwargs):
        activation_token = self.models.activationtoken.get(activationtoken)
        accountId = activation_token.accountId
        account = self.models.account.get(accountId)
        account.status = 'CONFIRMED'
        self.models.account.set(account)
        
        return True
        