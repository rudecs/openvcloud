from JumpScale import j
import time
import re
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor, wrap_remote

def _send_signup_mail(hrd, **kwargs):
    notifysupport = hrd.get("instance.openvcloud.cloudbroker.notifysupport")
    fromaddr = 'support@mothership1.com'
    toaddrs  =  [kwargs['email']]
    if notifysupport == '1':
        toaddrs.append('support@mothership1.com')


    html = """
<html>
<head></head>
<body>


    Dear,<br>
    <br>
    Thank you for registering with Mothership<sup>1</sup>.
    <br>
    <br>
    You can now log in into mothership<sup>1</sup> with your username %(username)s and your chosen password.
    <br>
    <br>
    In case you experience any issues in logging in or using the Mothership<sup>1</sup> service, please contact us at support@mothership1.com or use the live chat function on mothership1.com
    <br>
    <br>
    Best Regards,<br>
    <br>
    The Mothership<sup>1</sup> Team<br>
    <a href="%(portalurl)s">www.mothership1.com</a><br>
</body>
</html>
""" % kwargs

    j.clients.email.send(toaddrs, fromaddr, "Mothership1 account activation", html, files=None)


class cloudbroker_account(BaseActor):
    def __init__(self):
        super(cloudbroker_account, self).__init__()
        self.syscl = j.clients.osis.getNamespace('system')
        self.cloudapi = self.cb.actors.cloudapi

    def _checkAccount(self, accountname):
        account = self.models.account.simpleSearch({'name':accountname})
        if not account:
            raise exceptions.NotFound('Account name not found')
        if len(account) > 1:
            raise exceptions.BadRequest('Found multiple accounts for the account name "%s"' % accountname)

        return account[0]

    def _checkUser(self, username):
        user = self.syscl.user.simpleSearch({'id':username})
        if not user:
            raise exceptions.NotFound('Username "%s" not found' % username)
        return user[0]

    def _isValidUserName(self, username):
        r = re.compile('^[a-z0-9]{1,20}$')
        return r.match(username) is not None

    def _isValidPassword(self, password):
        if len(password) < 8 or len (password) > 80:
            return False
        return re.search(r"\s",password) is None

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def disable(self, accountname, reason, **kwargs):
        """
        Disable an account
        param:acountname name of the account
        param:reason reason of disabling
        result
        """
        account = self._checkAccount(accountname)
        msg = 'Account: %s\nReason: %s' % (accountname, reason)
        subject = 'Disabling account: %s' % accountname
        ticketId = j.tools.whmcs.tickets.create_ticket(subject, msg, 'High')
        account['deactivationTime'] = time.time()
        account['status'] = 'DISABLED'
        self.models.account.set(account)
        # stop all account's machines
        cloudspaces = self.models.cloudspace.search({'accountId': account['id']})[1:]
        for cs in cloudspaces:
            vmachines = self.models.vmachine.search({'cloudspaceId': cs['id'], 'status': 'RUNNING'})[1:]
            for vmachine in vmachines:
                self.cloudapi.machines.stop(vmachine['id'])
        j.tools.whmcs.tickets.close_ticket(ticketId)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def create(self, username, name, emailaddress, password, location, **kwargs):
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
            if not self.syscl.user.search({'id': username, 'emails': emailaddress})[1:]:
                ctx.start_response('409 Conflict', [])
                return 'The specific user and email do not match.'
        else:
            j.core.portal.active.auth.createUser(username, password, emailaddress, ['user'], None)

        now = int(time.time())

        location = location.lower()

        locationurl = j.apps.cloudapi.locations.getUrl()

        account = self.models.account.new()
        account.name = username
        account.creationTime = now
        account.DCLocation = location
        account.company = ''
        account.companyurl = ''
        account.status = 'CONFIRMED'
        account.displayname = name

        ace = account.new_acl()
        ace.userGroupId = username
        ace.type = 'U'
        ace.right = 'CXDRAU'
        accountid = self.models.account.set(account)[0]

        signupcredit = self.hrd.getFloat('instance.openvcloud.cloudbroker.signupcredit')
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

        self.cloudapi.cloudspaces.create(accountid, location, 'default', username, None, None)
        _send_signup_mail(hrd=self.hrd, username=username, user=name, email=emailaddress, portalurl=locationurl)

        return accountid

    @auth(['level1', 'level2', 'level3'])
    def enable(self, accountname, reason, **kwargs):
        """
        Enable an account
        param:acountname name of the account
        param:reason reason of enabling
        result
        """
        account = self._checkAccount(accountname)
        if account['status'] != 'DISABLED':
            raise exceptions.BadRequest('Account is not disabled')

        account['status'] = 'CONFIRMED'
        self.models.account.set(account)
        return True

    @auth(['level1', 'level2', 'level3'])
    def rename(self, accountname, name, **kwargs):
        """
        Rename an account
        param:accountname name of the account
        param:name new name of the account
        result
        """
        account = self._checkAccount(accountname)
        account['name'] = name
        self.models.account.set(account)
        return True

    @auth(['level1', 'level2', 'level3'])
    def delete(self, accountname, reason, **kwargs):
        """
        Complete delete an acount from the system
        """
        account = self._checkAccount(accountname)
        accountId = account['id']
        query = {'accountId': accountId, 'status': {'$ne': 'DESTROYED'}}
        cloudspaces = self.models.cloudspace.search(query)[1:]
        for cloudspace in cloudspaces:
            cloudspacename = cloudspace['name']
            cloudspaceid = cloudspace['id']
            j.apps.cloudbroker.cloudspace.destroy(accountname, cloudspacename, cloudspaceid, reason, **kwargs)
        account = self.models.account.get(accountId)
        account.status = 'DESTROYED'
        self.models.account.set(account)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def addUser(self, accountname, username, accesstype, **kwargs):
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        param:accountname id of the account
        param:username id of the user to give access
        param:accesstype 'R' for read only access, 'W' for Write access
        result bool
        """
        ctx = kwargs["ctx"]
        account = self._checkAccount(accountname)
        accountId = account['id']
        user = self._checkUser(username)
        userId = user['id']
        self.cloudapi.accounts.addUser(accountId, userId, accesstype)
        return True

    @auth(['level1', 'level2', 'level3'])
    @wrap_remote
    def deleteUser(self, accountname, username, **kwargs):
        """
        Delete a user from the account
        """
        ctx = kwargs["ctx"]
        account = self._checkAccount(accountname)
        accountId = account['id']
        user = self._checkUser(username)
        userId = user['id']
        self.cloudapi.accounts.deleteUser(accountId, userId)
        return True
