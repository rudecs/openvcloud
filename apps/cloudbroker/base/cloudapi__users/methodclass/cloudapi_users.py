from OpenWizzy import o
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

        pass

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
        if o.apps.system.usermanager.authenticate(username, password):
            session = ctx.env['beaker.get_session']() #create new session
            session['user'] = username
            session.save()
            return session.id
        else:
            ctx.start_response('401 Unauthorized', [])
            return

