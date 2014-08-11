from JumpScale import j


class auth(object):
    def __init__(self, acl):
        self.acl = set(acl)
        self._models = None

    @property
    def models(self):
        if not self._models:
            self._models = j.apps.cloud.cloudbroker.extensions.imp.getModel()
        return self._models

    def expandAclFromCloudspace(self, users, groups, cloudspace):
        fullacl = self.expandAcl(users, groups, cloudspace.acl)
        account = self.models.account.get(cloudspace.accountId)
        fullacl.update(self.expandAcl(users, groups, account.acl))
        return fullacl
    
    def expandAclFromAccount(self, users, groups, account):
        fullacl = self.expandAcl(users, groups, account.acl)
        return fullacl

    def expandAcl(self, user, groups, acl):
        fullacl = set()
        for ace in acl:
            right = set(ace.right)
            if ace.type == 'U' and ace.userGroupId == user:
                fullacl.update(right)
            elif ace.type == 'G' and ace.userGroupId in groups:
                fullacl.update(right)
        return fullacl

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if 'ctx' not in kwargs:
                # call is not performed over rest let it pass
                return func(*args, **kwargs)
            ctx = kwargs['ctx']
            user = ctx.env['beaker.session']['user']
            account_status = ctx.env['beaker.session'].get('account_status', 'CONFIRMED')
            if account_status != 'CONFIRMED':
              ctx.start_response('409 Conflict', [])
              return 'Unconfirmed Account'
            fullacl = set()
            if self.acl:
                userobj = j.core.portal.active.auth.getUserInfo(user)
                groups = userobj.groups
                # add brokeradmin access
                if 'admin' in groups:
                    return func(*args, **kwargs)
                cloudspace = None
                if 'accountId' in kwargs and kwargs['accountId']:
                    account = self.models.account.get(kwargs['accountId'])
                    fullacl.update(self.expandAclFromAccount(user, groups, account))
                elif 'cloudspaceId' in kwargs and kwargs['cloudspaceId']:
                    cloudspace = self.models.cloudspace.get(kwargs['cloudspaceId'])
                    fullacl.update(self.expandAclFromCloudspace(user, groups, cloudspace))
                elif 'machineId' in kwargs:
                    machine = self.models.vmachine.get(kwargs['machineId'])
                    cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
                    fullacl.update(self.expandAclFromCloudspace(user, groups, cloudspace))
                # if admin allow all other ACL as well
                if 'A' in fullacl:
                    fullacl.update('CXDRU')
                if cloudspace and not self.acl.issubset(fullacl):
                    ctx.start_response('403 No ace rule found for user %s for access %s' % (user, ''.join(self.acl)), [])
                    return ''
                elif ((not cloudspace and 'cloudspaceId' in kwargs) or 'S' in self.acl) and 'admin' not in groups:
                    ctx.start_response('403 Method requires admin privileges', [])
                    return ''

            return func(*args, **kwargs)
        return wrapper
