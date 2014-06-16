from JumpScale import j

class cloudbroker_user(j.code.classGetBase()):
    """
    Operator actions for interventions specific to a user
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="user"
        self.appname="cloudbroker"
        self._cb = None
        self.users = self.cb.extensions.imp.actors.cloudapi.users
        self.acl = j.clients.agentcontroller.get()

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

        pass

    def generateAuthorizationKey(self, username, reason, **kwargs):
        """
        Generates a valid authorizationkey in the context of a specific user.
        This key can be used in a webbrowser to browse the cloud portal from the perspective of that specific user or to use the api in his/her authorization context
        param:username name of the user an authorization key is required for
        param:reason reason
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method generateAuthorizationKey")
    
