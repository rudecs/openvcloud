from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
import JumpScale.grid.agentcontroller
import JumpScale.baselib.mailclient
from cloudbrokerlib.baseactor import BaseActor
import re, string, random, time
import json
import md5


VALIDATION_TIME = 7 * 24 * 60 * 60


class cloudapi_users(BaseActor):
    """
    User management

    """
    def __init__(self):
        super(cloudapi_users, self).__init__()
        self.libvirt_actor = j.apps.libcloud.libvirt
        self.acl = j.clients.agentcontroller.get()
        self.systemodel = j.clients.osis.getNamespace('system')

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
            try:
                data = json.loads(user.data)
            except:
                data = {}
            return {'username':user.id, 'emailaddresses': user.emails, 'data': data}
        else:
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    @audit()
    def setData(self, data, **kwargs):
        """
        Set user data
        param:username username of the user
        result:
        """
        ctx = kwargs['ctx']
        username = ctx.env['beaker.session']['user']
        if username == 'guest':
            ctx.start_response('403 Forbidden', [])
            return 'Forbidden'

        user = j.core.portal.active.auth.getUserInfo(username)
        if user:
            try:
                userdata = json.loads(user.data)
            except:
                userdata = {}
            userdata.update(data)
            user.data = json.dumps(userdata)
            self.systemodel.user.set(user)
            return True
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
                    user.passwd =  md5.new(newPassword).hexdigest()
                    self.systemodel.user.set(user)
                    return [200, "Your password has been changed."]
              else:
                 return [400, "Your current password doesn't match."]
        else:
            ctx = kwargs['ctx']
            ctx.start_response('404 Not Found', [])
            return 'User not found'

    def _sendResetPasswordMail(self, emailaddress, username, resettoken, portalurl):
        fromaddr = self.hrd.get('instance.openvcloud.supportemail')
        if isinstance(emailaddress, list):
            toaddrs = emailaddress
        else:
            toaddrs = [emailaddress]

        args = {
            'email': emailaddress,
            'username': username,
            'resettoken': resettoken,
            'portalurl': portalurl
        }

        message = j.core.portal.active.templates.render('cloudbroker/email/users/reset_password.html', **args)
        subject = j.core.portal.active.templates.render('cloudbroker/email/users/reset_password.subject.txt', **args)

        j.clients.email.send(toaddrs, fromaddr, subject, message, files=None)

    def sendResetPasswordLink(self, emailaddress, **kwargs):
        """
        Sends a reset password link to the supplied email address
        param:emailaddress unique emailaddress for the account
        result bool
        """
        ctx = kwargs['ctx']

        existingusers = self.systemodel.user.search({'emails':emailaddress})[1:]

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

        user = self.systemodel.user.get(actual_reset_token.userguid)
        user.passwd = md5.new(newpassword).hexdigest()
        self.systemodel.user.set(user)

        self.models.resetpasswordtoken.delete(resettoken)

        return [200, "Your password has been changed."]

    def validate(self, validationtoken, password, **kwargs):
        ctx = kwargs['ctx']

        tokens = self.models.resetpasswordtoken.search({'id': validationtoken})[1:]
        if not tokens:
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        activation_token = tokens[0]

        if activation_token['creationTime'] + VALIDATION_TIME < time.time():  # time has passed.
            ctx.start_response('419 Authentication Expired', [])
            return 'Invalid or expired validation token'

        user = self.systemodel.user.get(activation_token['username'])
        user.passwd = md5.new(password).hexdigest()
        self.systemodel.user.set(user)

        # Invalidate the token.
        activation_token['creationTime'] = 0
        self.models.resetpasswordtoken.set(activation_token)

        return True
