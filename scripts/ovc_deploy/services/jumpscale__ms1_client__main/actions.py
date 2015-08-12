from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    """
    """
    def configure(self,serviceObj):
        """
        configure ms1
        """
        import JumpScale.lib.ms1

        secret=j.tools.ms1.getCloudspaceSecret("christophe","OshotsAg5","ovc_deploy","eu1")

        #this remembers the secret required to use ms1
        serviceObj.hrd.set("instance.param.secret",secret)

        return True

