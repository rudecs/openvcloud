from JumpScale import j
from .cloudbroker import models


class auth(object):

    def __init__(self, acl):
        self.acl = set(acl)
        self.models = models

    def getAccountAcl(self, accountId):
        result = dict()
        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.type == 'U':
                ace_dict = dict(userGroupId=ace.userGroupId, right=set(ace.right), type='U', canBeDeleted=True)
                result[ace.userGroupId] = ace_dict
        return result

    def getCloudspaceAcl(self, cloudspaceId):
        result = dict()
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        for ace in cloudspace.acl:
            if ace.type == 'U':
                ace_dict = dict(userGroupId=ace.userGroupId, right=set(ace.right), type='U', canBeDeleted=True)
                result[ace.userGroupId] = ace_dict

        for user_id, ace in self.getAccountAcl(cloudspace.accountId).iteritems():
            if user_id in result:
                result[user_id]['canBeDeleted'] = False
                result[user_id]['right'].update(ace['right'])
            else:
                ace['canBeDeleted'] = False
                result[user_id] = ace
        return result

    def getVMachineAcl(self, machineId):
        result = dict()
        machine = self.models.vmachine.get(machineId)
        for ace in machine.acl:
            if ace.type == 'U':
                ace_dict = dict(userGroupId=ace.userGroupId, right=set(ace.right), type='U', canBeDeleted=True)
                result[ace.userGroupId] = ace_dict

        for user_id, ace in self.getCloudspaceAcl(machine.cloudspaceId).iteritems():
            if user_id in result:
                result[user_id]['canBeDeleted'] = False
                result[user_id]['right'].update(ace['right'])
            else:
                ace['canBeDeleted'] = False
                result[user_id] = ace
        return result

    def expandAclFromVMachine(self, users, groups, vmachine):
        fullacl = self.expandAcl(users, groups, vmachine.acl)
        cloudspace = self.models.cloudspace.get(vmachine.cloudspaceId)
        fullacl.update(self.expandAclFromCloudspace(users, groups, cloudspace))
        return fullacl

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
                account = None
                cloudspace = None
                machine = None
                if 'accountId' in kwargs and kwargs['accountId']:
                    account = self.models.account.get(int(kwargs['accountId']))
                    fullacl.update(self.expandAclFromAccount(user, groups, account))
                elif 'cloudspaceId' in kwargs and kwargs['cloudspaceId']:
                    cloudspace = self.models.cloudspace.get(int(kwargs['cloudspaceId']))
                    fullacl.update(self.expandAclFromCloudspace(user, groups, cloudspace))
                elif 'machineId' in kwargs and kwargs['machineId']:
                    machine = self.models.vmachine.get(int(kwargs['machineId']))
                    fullacl.update(self.expandAclFromVMachine(user, groups, machine))
                # if admin allow all other ACL as well
                if 'A' in fullacl:
                    fullacl.update('CXDRU')
                if ((cloudspace or account or machine) and not self.acl.issubset(fullacl)):
                    ctx.start_response('403 Forbidden', [])
                    return str('User: "%s" isn\'t allowed to execute this action. No enough permissions' % user)
                elif ((not cloudspace and 'cloudspaceId' in kwargs) or 'S' in self.acl) and 'admin' not in groups:
                    ctx.start_response('403 Forbidden', [])
                    return str('Method requires "admin" privileges')

            return func(*args, **kwargs)
        return wrapper
