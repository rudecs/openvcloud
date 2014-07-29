from JumpScale import j
from JumpScale import portal
import ujson

class pricing(object):
    def __init__(self):

        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass

        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.cloudbrokermodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.cloudbrokermodels.__dict__[ns].find = self.cloudbrokermodels.__dict__[ns].search

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
            query = {'fields': ['id', 'memory']}
            results  = self.cloudbrokermodels.size.find(ujson.dumps(query))['result']
            self._machine_sizes = dict([(res['fields']['id'], res['fields']) for res in results])
        return self._machine_sizes


    @property
    def machine_images(self):
        if not self._machine_images:
            query = {'fields': ['id', 'type','name']}
            results  = self.cloudbrokermodels.image.find(ujson.dumps(query))['result']
            self._machine_images = dict([(res['fields']['id'], res['fields']) for res in results])
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

    def get_burn_rate(self, accountId):
        burn_rate_report = {'accountId':accountId, 'cloudspaces':[]}
        query = {'fields': ['id', 'name', 'accountId']}
        query['query'] = {'term': {'accountId': accountId}}
        results = self.cloudbrokermodels.cloudspace.find(ujson.dumps(query))['result']
        cloudspaces = [res['fields'] for res in results]

        account_hourly_cost = 0.0

        for cloudspace in cloudspaces:
            query = {'fields':['id','deletionTime','name','cloudspaceId','imageId','sizeId','disks']}

            query['query'] = {'filtered':{
                          "query" : {"term" : { "cloudspaceId" : cloudspace['id'] }},
                          "filter" : { "not":{"range" : {"deletionTime" : {"gt":0}}}
                                      }
                                 }
                              }

            queryresult = self.cloudbrokermodels.vmachine.find(ujson.dumps(query))['result']
            machines = [res['fields'] for res in queryresult]

            if len(machines) is 0:
                continue

            cloudspace_hourly_cost = 0.0

            for machine in machines:
                cloudspace_hourly_cost += self.get_machine_price_per_hour(machine)

            burn_rate_report['cloudspaces'].append({'id':cloudspace['id'],'name':cloudspace['name'],'hourlyCost':cloudspace_hourly_cost})

            account_hourly_cost += cloudspace_hourly_cost

        burn_rate_report['hourlyCost'] = account_hourly_cost

        return burn_rate_report
