from JumpScale import j
import os
import datetime
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_logs(BaseActor):
    """
    Create logging for accounts including cloudspaces and machines
    """
    def __init__(self):
        super(cloudapi_logs, self).__init__()
        self.basedir = "/opt/jumpscale7/var/log/cloudunits"
        self.model = j.clients.osis.getNamespace('cloudbroker')
        self.memsizes = {s['id']: s['memory'] for s in
                    self.models.size.search({'$fields': ['id', 'memory']})[1:]}
        self.cpusizes = {s['id']: s['vcpus'] for s in
                    self.models.size.search({'$fields': ['id', 'vcpus']})[1:]}
        self.disksizes = {d['id']: d['sizeMax'] for d in self.models.disk.search(
            {'$query': {'status': {'$ne': 'DESTROYED'}},
             '$fields': ['id', 'sizeMax']}, size=0)[1:]}

    @audit()
    def logCloudUnits(self, **kwargs):
        """
        result bool
        """
        currenttime = datetime.datetime.now()
        year = currenttime.year
        month = currenttime.month
        day = currenttime.day
        hour = currenttime.hour
        minute = currenttime.minute

        accounts = self.model.account.search({'$fields': ['id', 'name'], '$query': {'status': {'$ne': 'DESTROYED'}}}, size=0)[1:]
        for account in accounts:
            accountpath = os.path.join(self.basedir, "%s/%s/%s/%s" % (account['id'], year, month, day))
            # create path if it doesn't exists
            if not os.path.exists(accountpath):
                os.makedirs(accountpath)
            account_log = {'account': account['id'], 'name': account['name']}
            consumed_dict = j.apps.cloudapi.accounts.getConsumedCloudUnits(account['id'])
            account_log.update(consumed_dict)
            account_log['cloudspaces'] = list()
            query = {'accountId': account['id'], 'status': {'$ne': 'DESTROYED'}}
            cloudspaces = self.models.cloudspace.search({'$fields': ['id', 'name'], '$query': query})[1:]
            for cloudspace in cloudspaces:
                cloudspace_dict = j.apps.cloudapi.cloudspaces.getConsumedCloudUnits(cloudspace['id'])
                cloudspace_dict['cloudspaceId'] = cloudspace['id']
                cloudspace_dict['name'] = cloudspace['name']
                cloudspace_dict['machines'] = list()
                machines = self.models.vmachine.search({'$fields': ['id', 'name', 'sizeId', 'disks', 'nics'],
                                                        '$query': {'cloudspaceId': cloudspace['id'],
                                                                   'status': {
                                                                       '$nin': ['DESTROYED', 'ERROR']}}},
                                                       size=0)[1:]
                for machine in machines:
                    machine_dict = dict()
                    machine_dict['name'] = machine['name']
                    machine_dict['id'] = machine['id']
                    machine_dict['CU_M'] = self.memsizes[machine['sizeId']]
                    machine_dict['CU_C'] = self.cpusizes[machine['sizeId']]
                    machine_dict['CU_D'] = 0
                    machine_dict['CU_I'] = 0
                    for diskid in machine['disks']:
                        machine_dict['CU_D'] += self.disksizes[diskid]
                    cloudspace_dict['machines'].append({machine['id']: machine_dict})
                    for nic in machine["nics"]:
                        if nic["type"] == "PUBLIC":
                            machine_dict['CU_I'] += 1

                account_log['cloudspaces'].append({cloudspace['id']: cloudspace_dict})

            with open("%s/%s_%s.json" % (accountpath, hour, minute), 'w+') as f:
                f.write(str(account_log))
        return True
