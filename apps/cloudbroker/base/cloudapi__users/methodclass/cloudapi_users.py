from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
import JumpScale.grid.agentcontroller
import re, string, random, time
import md5

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
        self.libcloud_model = j.core.osis.getClientForNamespace('libcloud')

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
            return 'User already exists'
        else:
            now = int(time.time())

            location = location.lower()

            if not location in self.cb.extensions.imp.getLocations():
                location = self.cb.extensions.imp.whereAmI()

            locationurl = self.cb.extensions.imp.getLocations()[location]
            if location != self.cb.extensions.imp.whereAmI():
                correctlocation = "%s/restmachine/cloudapi/users/register" % (locationurl)
                ctx.start_response('451 Redirect', [('Location', correctlocation)])
                return 'The request has been made on the wrong location, it should be done where the cloudspace needs to be created, in this case %s' % correctlocation
            networkids = self.libcloud_model.libvirtdomain.get('networkids')

            if (len(networkids) < 25) or (j.application.config.exists('mothership1.cloudbroker.disableregistration') and j.application.config.getInt('mothership1.cloudbroker.disableregistration') == 1):
                userdata = {'username':username,'user': user, 'emailaddress': emailaddress, 'password': password, 'company': company, 'companyurl': companyurl, 'location': location, 'promocode': promocode}
                with open('/root/logs/request_access/%s.json' % emailaddress, 'w') as fd:
                    json.dump(userdata, fd)
                fromaddr = 'support@mothership1.com'
                toaddrs = emailaddress
                html = """
<html>

<head></head>

<body>

Dear,<br>

<br>

Thank you for registering with Mothership<sup>1</sup>.<br>

<br>

As we prefer to verify and follow up the experience of our new customers, we schedule new arrivals in batches.<br>

<br>

As there are currently many new registrations, you are queued to be provisioned in the next batches.<br>

<br>

Thank you for your understanding and we hope to see you soon on Mothership<sup>1</sup>.<br>

<br>

Best Regards,<br>

<br>

The Mothership<sup>1</sup> Team<br>

www.mothership1.com<br>

</body>

</html>
"""
                j.clients.email.send(toaddrs, fromaddr, "Mothership1 account activation", html, files=None)
                return True

                

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
            if promocode == 'cloud50':
                signupcredit = 50.0
                creditcomment = 'Promo code cloud50'
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

            args = {'accountid': accountid, 'password': password, 'email': emailaddress, 'now': now, 'portalurl': locationurl, 'token': actual_token, 'username':username, 'user': user}
            self.acl.executeJumpScript('cloudscalers', 'cloudbroker_accountcreate', queue='hypervisor', args=args, nid=j.application.whoAmI.nid, wait=False)

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
