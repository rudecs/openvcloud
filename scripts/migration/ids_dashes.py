from pymongo import  MongoClient
client = MongoClient('localhost')
db = client['libvirt']
nodes = db['node']
for node in nodes.find():
    if '-' not in node['guid']:

        node['guid'] = "%s-%s-%s-%s-%s" % (node['guid'][0:8], node['guid'][8:12], node['guid'][12:16], node['guid'][16:20], node['guid'][20:])
        node['id'] = node['guid']
        nodes.save(node)


db = client['libcloud']
domains = db['libvirtdomain']
for domain in domains.find():
    if domain['guid'].startswith('domain') and '-' not in domain['guid']:
        id = domain['_id']
        domain['guid'] = "%s-%s-%s-%s-%s" % (domain['guid'][0:15], domain['guid'][15:19], domain['guid'][19:23], domain['guid'][23:27], domain['guid'][27:])
        domain['_id'] = domain['guid']
        domains.save(domain)
        domains.delete_one({'_id': id})

client.cloudbroker.account.update({"updateTime": None}, {"$set": {"updateTime": "N/A"}})
client.cloudbroker.vmachine.update({"updateTime": None}, {"$set": {"updateTime": "N/A"}})
client.cloudbroker.cloudspace.update({"updateTime": None}, {"$set": {"updateTime": "N/A"}})
