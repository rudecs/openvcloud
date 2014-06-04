from JumpScale import j

class cloudbroker_cloudspace(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="cloudspace"
        self.appname="cloudbroker"
        self._cb = None
        self._models = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    def destroy(self, accountname, cloudspaceName, cloudspaceId, reason, **kwargs):
        accounts = self.models.account.simpleSearch({'name':accountname})
        if not accounts:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'

        accountid = accounts[0]['id']

        cloudspaces = self.models.cloudspace.simpleSearch({'name': cloudspaceName, 'id': cloudspaceId, 'accountId': accountid})
        if not cloudspaces:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Cloudspace with name %s and id %s that has account %s not found' % (cloudspaceName, cloudspaceId, accountname)

        cloudspace = cloudspaces[0]

        if str(cloudspace['location']) != j.application.config.get('cloudbroker.where.am.i'):
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'),]
            ctx.start_response("302", headers)
            return 'Cloudspace is not in this location. In %s.' % cloudspace['location']

        cloudspace['status'] = 'DESTROYED'
        self.models.cloudspace.set(cloudspace)