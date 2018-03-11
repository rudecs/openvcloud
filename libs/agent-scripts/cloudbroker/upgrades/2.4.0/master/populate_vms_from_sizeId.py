from JumpScale import j

descr = """
Upgrade script
Add privatenetwork field
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
roles = ['master']
async = True

def action():
    cbcl = j.clients.osis.getNamespace('cloudbroker')
    for machine in cbcl.vmachine.search({'$fields': ['id', 'sizeId', 'memory', 'vcpus'], 
                                                '$query': {'sizeId': {'$ne': 0}}}, size=0)[1:]:
        size = cbcl.size.get(machine['sizeId'])
        update = {'memory': machine['memory']  if machine.get('memory') else size.memory ,
                    'vcpus': machine['vcpus'] if machine.get('vcpus') else size.vcpus}
        cbcl.vmachine.updateSearch({'id': machine['id']},  {'$set': update})
