from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
import JumpScale.grid.agentcontroller
import JumpScale.baselib.mailclient
from cloudbrokerlib.baseactor import BaseActor
import re, string, random, time
import md5

class cloudapi_users(BaseActor):
    """
    User management

    """
    def __init__(self):
        super(cloudapi_users, self).__init__()
        self.libvirt_actor = j.apps.libcloud.libvirt
        self.acl = j.clients.agentcontroller.get()

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
        accounts = self.models.account.search({'name':username})[1:]
        if accounts:
            status = accounts[0].get('status', 'CONFIRMED')
            if j.core.portal.active.auth.authenticate(username, password):
                session = ctx.env['beaker.get_session']() #create new session
                session['user'] = username
                session['account_status'] = status
                session.save()
                if status != 'CONFIRMED':
                    ctx.start_response('409 Conflict', [])
                    return session.id
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
                    cl = j.clients.osis.getByInstance('main')
                    usercl = j.clients.osis.getCategory(cl, 'system', 'user')
                    user.passwd =  md5.new(newPassword).hexdigest()
                    usercl.set(user)
                    return [200, "Your password has been changed."]
              else:
                 return [400, "Your current password doesn't match."]
        else:
            ctx = kwargs['ctx']
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    def _sendResetPasswordMail(self, emailaddress, username, resettoken, portalurl):
        
        fromaddr = 'support@mothership1.com'
        toaddrs  =  [emailaddress]

        html = """
<html>
<head></head>
<body>


    Dear,<br>
    <br>
    A request for a password reset on the Mothership<sup>1</sup> service has been requested using this email address.
    <br>
    <br>
    You can set a new password for the user %(username)s using the following link: <a href="%(portalurl)s/wiki_gcb/ResetPassword?token=%(resettoken)s">%(portalurl)s/wiki_gcb/ResetPassword?token=%(resettoken)s</a>
    <br>
    If you are unable to follow the link, copy and paste it in your favorite browser.
    <br>
    <br>
    <br>
    In case you experience any more issues logging in or using the Mothership<sup>1</sup> service, please contact us at support@mothership1.com or use the live chat function on mothership1.com
    <br>
    <br>
    Best Regards,<br>
    <br>
    The Mothership<sup>1</sup> Team<br>
    <a href="%(portalurl)s">www.mothership1.com</a><br>
</body>
</html>
    """ % {'email':emailaddress, 'username':username, 'resettoken':resettoken, 'portalurl':portalurl}

        j.clients.email.send(toaddrs, fromaddr, "Your Mothership1 password reset request", html, files=None)

    def sendResetPasswordLink(self, emailaddress, **kwargs):
        """
        Sends a reset password link to the supplied email address
        param:emailaddress unique emailaddress for the account
        result bool
        """
        ctx = kwargs['ctx']
        
        cl = j.clients.osis.getNamespace('system')
        existingusers = cl.user.search({'emails':emailaddress})[1:]

        if (len(existingusers) == 0):
            ctx.start_response('404 Not Found', [])
            return 'No user has been found for this email address'
        
        user = existingusers[0]
        locationurl = j.apps.cloudapi.locations.getUrl()
        #create reset token
        actual_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(64))
        reset_token = self.models.resetpasswordtoken.new()
        reset_token.id = actual_token
        reset_token.creationTime = int(time.time())
        reset_token.username = user['id']
        reset_token.userguid = user['guid']
        self.models.resetpasswordtoken.set(reset_token)

        self._sendResetPasswordMail(emailaddress,user['id'],actual_token,locationurl)
        
        return 'Reset password email send'

    def getResetPasswordInformation(self, resettoken, **kwargs):
        """
        Retrieve information about a password reset token (if still valid)
        param:resettoken password reset token
        result bool
        """
        ctx = kwargs['ctx']
        now = int(time.time())
        if not self.models.resetpasswordtoken.exists(resettoken):
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        actual_reset_token = self.models.resetpasswordtoken.get(resettoken)

        if (actual_reset_token.creationTime + 900) < now:
            self.models.resetpasswordtoken.delete(resettoken)
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        return {'username':actual_reset_token.username}

    def resetPassword(self, resettoken, newpassword, **kwargs):
        """
        Resets a password
        param:resettoken password reset token
        param:newpassword new password
        result bool
        """
        ctx = kwargs['ctx']
        now = int(time.time())
        if not self.models.resetpasswordtoken.exists(resettoken):
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        if not self._isValidPassword(newpassword):
            ctx.start_response('409 Bad Request', [])
            return '''A password must be at least 8 and maximum 80 characters long
                      and may not contain whitespace'''

        actual_reset_token = self.models.resetpasswordtoken.get(resettoken)

        if (actual_reset_token.creationTime + 900 + 120) < now:
            self.models.resetpasswordtoken.delete(resettoken)
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        systemcl = j.clients.osis.getNamespace('system')
        user = systemcl.user.get(actual_reset_token.userguid)
        user.passwd =  md5.new(newpassword).hexdigest()
        systemcl.user.set(user)
        
        self.models.resetpasswordtoken.delete(resettoken)
        
        return [200, "Your password has been changed."]

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
