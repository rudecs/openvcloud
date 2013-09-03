from JumpScale import j


class auth(object):
    def __init__(self, acl):
        self.acl = set(acl)

    def expandAclFromCloudspace(self, users, groups, cloudspace):
        fullacl = self.expandAcl(users, groups, cloudspace['acl'])
        account = j.apps.cloud.cloudbroker.model_account_get(cloudspace['accountId'])
        fullacl.update(self.expandAcl(users, groups, account['acl']))
        return fullacl

    def expandAcl(self, user, groups, acl):
        fullacl = set()
        for ace in acl:
            right = set(ace['right'])
            if ace['type'] == 'U' and ace['userGroupId'] == user:
                fullacl.update(right)
            elif ace['type'] == 'G' and ace['userGroupId'] in groups:
                fullacl.update(right)
        return fullacl

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            ctx = kwargs['ctx']
            user = ctx.env['beaker.session']['user']
            fullacl = set()
            if self.acl:
                groups = j.apps.system.usermanager.getusergroups(user)
                # add brokeradmin access
                if 'admin' in groups:
                    return func(*args, **kwargs)
                cloudspace = None
                if 'cloudspaceId' in kwargs and kwargs['cloudspaceId']:
                    cloudspace = j.apps.cloud.cloudbroker.model_cloudspace_get(kwargs['cloudspaceId'])
                    fullacl.update(self.expandAclFromCloudspace(user, groups, cloudspace))
                elif 'machineId' in kwargs:
                    machine = j.apps.cloud.cloudbroker.mode_vmachine_get(kwargs['machineId'])
                    cloudspace = j.apps.cloud.cloudbroker.model_cloudspace_get(machine['cloudspaceId'])
                    fullacl.update(self.expandAclFromCloudspace(user, groups, cloudspace))
                # if admin allow all other ACL as well
                if 'A' in fullacl:
                    fullacl.update('CXDRU')
                if cloudspace and not self.acl.issubset(fullacl):
                    ctx.start_response('403 No ace rule found for user %s for access %s' % (user, ''.join(self.acl)), [])
                    return
                elif ((not cloudspace and 'cloudspaceId' in kwargs) or 'S' in self.acl) and 'admin' not in groups:
                    ctx.start_response('403 Method requires admin privileges', [])
                    return

            return func(*args, **kwargs)
        return wrapper

