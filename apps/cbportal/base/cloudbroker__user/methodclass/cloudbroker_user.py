from JumpScale import j
import JumpScale.grid.osis

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
        self.users_actor = self.cb.extensions.imp.actors.cloudapi.users

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    def generateAuthorizationKey(self, username, **kwargs):
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        param:username name of the user an authorization key is required for
        """
        gid = j.application.whoAmI.gid
        user_guid = '%s_%s' % (gid, username)
        if not self.syscl.user.exists(user_guid):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'User %s does not exist' % username

        user = self.syscl.user.get(user_guid)
        return self.users_actor.authenticate(username, user.passwd)
