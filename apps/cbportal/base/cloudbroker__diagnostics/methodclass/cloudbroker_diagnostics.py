from cloudbrokerlib.authenticator import auth
from cloudbrokerlib.baseactor import BaseActor

class cloudbroker_diagnostics(BaseActor):
    """
    Operator actions to perform specific diagnostic checks on the platform
    
    """
    @auth(groups=['level1', 'level2', 'level3'])
    def checkVms(self, **kwargs):
        """
        Starts the vms check jumpscipt to do a ping to every VM from their virtual firewalls
        result boolean
        """
        return self.cb.executeJumpscript('jumpscale', 'vms_check', role='master')
