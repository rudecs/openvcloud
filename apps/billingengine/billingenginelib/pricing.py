from JumpScale import j
from JumpScale import portal
from JumpScale.grid import osis
import ujson

class pricing(object):
    def __init__(self):

        self.cloudbrokermodels = j.core.osis.getClientForNamespace('cloudbroker')
        self.base_machine_prices = {}

        for machine_price_key in j.application.config.getKeysFromPrefix('mothership1.billing.machineprices'):
            machine_type = machine_price_key.split('.')[-1]
            stringprices = j.application.config.getDict(machine_price_key)
            self.base_machine_prices[machine_type.lower()] = dict([(int(kv[0]),float(kv[1])) for kv in stringprices.items()])

        self.primary_storage_price = j.application.config.getFloat('mothership1.billing.primarystorageprice')
        self.extra_cloudspace_price = j.application.config.getFloat('mothership1.billing.extracloudspaceprice')

        self._machine_sizes = None
        self._machine_images = None

    @property
    def machine_sizes(self):
        if not self._machine_sizes:
            results  = self.cloudbrokermodels.size.search({})[1:]
            self._machine_sizes = {size['id']: size for size in results}
        return self._machine_sizes


    @property
    def machine_images(self):
        if not self._machine_images:
            results  = self.cloudbrokermodels.image.search({})[1:]
            self._machine_images = {size['id']: size for size in results}
        return self._machine_images


    def get_price_per_hour(self, imageId, sizeId, diskSize):
        machine_memory = self.machine_sizes[int(sizeId)]['memory']
        machine_type = 'Linux'
        if self.machine_images.has_key(int(imageId)):
            machine_type = self.machine_images[int(imageId)]['type']
        if not self.base_machine_prices.has_key(machine_type):
            machine_type = 'Linux'

        base_price = self.base_machine_prices[machine_type.lower()][machine_memory]
        storage_price = (int(diskSize) - 10) * self.primary_storage_price
        return base_price + storage_price

    def get_cloudspace_price_per_hour(self):
        return self.extra_cloudspace_price

    def get_machine_price_per_hour(self, machine):
        machine_imageId = machine['imageId']
        machine_sizeId = machine['sizeId']
        diskId = machine['disks'][0]
        disk = self.cloudbrokermodels.disk.get(diskId)
        diskSize = disk.sizeMax

        return self.get_price_per_hour(machine_imageId, machine_sizeId, diskSize)

    def _listActiveCloudSpaces(self, accountId):
        query = {'accountId': accountId, 'status': {'$ne': 'DESTROYED'}}
        cloudspaces = self.cloudbrokermodels.cloudspace.search(query)[1:]
        return cloudspaces

    def get_burn_rate(self, accountId):
        burn_rate_report = {'accountId':accountId, 'cloudspaces':[]}
        cloudspaces = self._listActiveCloudSpaces(accountId)

        account_hourly_cost = (len(cloudspaces) - 1) * self.get_cloudspace_price_per_hour()

        for cloudspace in cloudspaces:
            query = {'cloudspaceId': cloudspace['id'], 'status': {'$nin': ['DESTROYING', 'DESTROYED']}}
            machines = self.cloudbrokermodels.vmachine.search(query)[1:]

            if len(machines) is 0:
                continue

            cloudspace_hourly_cost = 0.0

            for machine in machines:
                cloudspace_hourly_cost += self.get_machine_price_per_hour(machine)

            burn_rate_report['cloudspaces'].append({'id':cloudspace['id'],'name':cloudspace['name'],'hourlyCost':cloudspace_hourly_cost})

            account_hourly_cost += cloudspace_hourly_cost

        burn_rate_report['hourlyCost'] = account_hourly_cost

        return burn_rate_report
