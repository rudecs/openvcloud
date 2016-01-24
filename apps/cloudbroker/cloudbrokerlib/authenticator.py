from JumpScale import j
from JumpScale.portal.portal import exceptions
from .cloudbroker import models


class auth(object):

    def __init__(self, acl=None, level=None):
        self.acl = acl or dict()
        for key in self.acl:
            if key not in ['account', 'cloudspace', 'machine']:
                raise ValueError('Unexpected resource type specified in acl dict, only account, '
                                 'cloudspace and machine are allowed.')
        self.level = level
        self.models = models

    def getAccountAcl(self, accountId):
        result = dict()
        account = self.models.account.get(accountId)
        for ace in account.acl:
            if ace.type == 'U':
                ace_dict = dict(userGroupId=ace.userGroupId, account_right=set(ace.right), right=set(ace.right), type='U', canBeDeleted=True)
                result[ace.userGroupId] = ace_dict
        return result

    def getCloudspaceAcl(self, cloudspaceId):
        result = dict()
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        for ace in cloudspace.acl:
            if ace.type == 'U':
                ace_dict = dict(userGroupId=ace.userGroupId, cloudspace_right=set(ace.right), right=set(ace.right), type='U', canBeDeleted=True)
                result[ace.userGroupId] = ace_dict

        for user_id, ace in self.getAccountAcl(cloudspace.accountId).iteritems():
            if user_id in result:
                result[user_id]['canBeDeleted'] = False
                result[user_id]['right'].update(ace['right'])
                result[user_id]['account_right'] = ace['account_right']
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
        if not self.level or self.level == 'machine':
            fullacl = self.expandAcl(users, groups, vmachine.acl)
        else:
            fullacl = set()
        cloudspace = self.models.cloudspace.get(vmachine.cloudspaceId)
        fullacl.update(self.expandAclFromCloudspace(users, groups, cloudspace))
        return fullacl

    def expandAclFromCloudspace(self, users, groups, cloudspace):
        if not self.level or self.level == 'cloudspace':
            fullacl = self.expandAcl(users, groups, cloudspace.acl)
        else:
            fullacl = set()
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
                raise exceptions.Forbidden('Unconfirmed Account')
            account = None
            cloudspace = None
            machine = None
            if self.acl:
                if 'machineId' in kwargs and kwargs['machineId']:
                    machine = self.models.vmachine.get(int(kwargs['machineId']))
                    cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
                    account = self.models.account.get(cloudspace.accountId)
                elif 'diskId' in kwargs and kwargs['diskId']:
                    disk = self.models.disk.get(int(kwargs['diskId']))
                    machines = self.models.vmachine.search({'disks': disk.id,
                                                            'status': {'$ne': 'DESTROYED'}})[1:]
                    if machines:
                        machine = self.models.vmachine.get(machines[0]['id'])
                        cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
                    account = self.models.account.get(disk.accountId)
                elif 'imageid' in kwargs and kwargs['imageid']:
                    image = self.models.image.get(int(kwargs['imageid']))
                    account = self.models.account.get(image.accountId)
                elif 'cloudspaceId' in kwargs and kwargs['cloudspaceId']:
                    cloudspace = self.models.cloudspace.get(int(kwargs['cloudspaceId']))
                    account = self.models.account.get(cloudspace.accountId)
                elif 'accountId' in kwargs and kwargs['accountId']:
                    account = self.models.account.get(int(kwargs['accountId']))

            if self.isAuthorized(user, machine, cloudspace, account):
                return func(*args, **kwargs)
            else:
                raise exceptions.Forbidden(
                        '''User: "%s" isn't allowed to execute this action.
                        Not enough permissions''' % user)
        return wrapper

    def isAuthorized(self, username, machine=None, cloudspace=None, account=None):
        """
        Check if a user has the authorization to access a resource

        :param username: username of the user to be checked
        :param machine: machine object if authorization should be done on machine level
        :param cloudspace: cloudspace object if authorization should be done on cloudspace level
        :param account: account object if authorization should be done on account level
        :return: True if username is authorized to access the resource, False otherwise
        """
        userobj = j.core.portal.active.auth.getUserInfo(username)
        if not userobj.active:
            raise exceptions.Forbidden('User is not allowed to execute action while status is '
                                       'inactive.')
        groups = userobj.groups
        # add brokeradmin access
        if 'admin' in groups:
            return True

        if 'account' in self.acl and account:
            grantedaccountacl  = self.expandAclFromAccount(username, groups, account)
            if self.acl['account'].issubset(grantedaccountacl):
                return True
        if 'cloudspace' in self.acl and cloudspace:
            grantedcloudspaceacl = self.expandAclFromCloudspace(username, groups, cloudspace)
            if self.acl['cloudspace'].issubset(grantedcloudspaceacl):
                return True
        if 'machine' in self.acl and machine:
            grantedmachineacl = self.expandAclFromVMachine(username, groups, machine)
            if self.acl['machine'].issubset(grantedmachineacl):
                return True

        return False
