import os
import json
import datetime
from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib.baseactor import BaseActor

class cloudapi_logs(BaseActor):
    """
    Create logging for accounts including cloudspaces and machines
    """
    def __init__(self):
        super(cloudapi_logs, self).__init__()
        self.basedir = "/opt/jumpscale7/var/log/cloudunits"
        self.model = j.clients.osis.getNamespace('cloudbroker')

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

        disksizes = {d['id']: d['sizeMax'] for d in self.models.disk.search(
            {'$query': {'status': {'$ne': 'DESTROYED'}},
             '$fields': ['id', 'sizeMax']}, size=0)[1:]}

        memsizes = {s['id']: s['memory'] for s in
                    self.models.size.search({'$fields': ['id', 'memory']})[1:]}
        cpusizes = {s['id']: s['vcpus'] for s in
                    self.models.size.search({'$fields': ['id', 'vcpus']})[1:]}
        images = {s['id']: s['name'] for s in
                  self.models.image.search({'$fields': ['id', 'name']})[1:]}
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
                machines = self.models.vmachine.search({'$fields': ['id', 'name', 'sizeId', 'disks', 'nics', 'imageId'],
                                                        '$query': {'cloudspaceId': cloudspace['id'],
                                                                   'status': {'$nin': ['DESTROYED', 'ERROR']}
                                                                  }
                                                       },
                                                       size=0)[1:]
                for machine in machines:
                    machine_dict = dict()
                    machine_dict['name'] = machine['name']
                    machine_dict['imagename'] = images[machine['imageId']]
                    machine_dict['id'] = machine['id']
                    machine_dict['CU_M'] = memsizes[machine['sizeId']]
                    machine_dict['CU_C'] = cpusizes[machine['sizeId']]
                    machine_dict['CU_D'] = 0
                    machine_dict['CU_I'] = 0
                    for diskid in machine['disks']:
                        machine_dict['CU_D'] += disksizes[diskid]

                    for nic in machine["nics"]:
                        if nic["type"] == "PUBLIC":
                            machine_dict['CU_I'] += 1

                    cloudspace_dict['machines'].append({machine['id']: machine_dict})
                account_log['cloudspaces'].append({cloudspace['id']: cloudspace_dict})
            with open("%s/%s_%s_%s_%s_%s.json" % (accountpath, year, month, day, hour, minute), 'w+') as f:
                json.dump(account_log, f)
        return True
