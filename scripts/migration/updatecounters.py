#!/usr/bin/env python
from JumpScale import j
import JumpScale.grid.mongodbclient
import JumpScale.grid.osis
import pymongo

j.application.start('migratecount')

config = j.application.config
host = config.get('mongodb.host') if config.exists('mongodb.host') else 'localhost'
port = config.getInt('mongodb.port') if config.exists('mongodb.port') else 27017
mongodb_client = j.clients.mongodb.get(host, port)
client = j.core.osis.getClient(user='root')

namespace = 'cloudbroker'

for category in client.listNamespaceCategories(namespace):
    ids = client.list(namespace, category)
    maxid = 0
    if ids:
        maxid = max(ids) + 1
    count = mongodb_client[namespace]['counter'].find_one({'_id': category})
    count['seq'] = maxid
    print 'Setting count for %s to %s' % (category, maxid)
    mongodb_client[namespace]['counter'].save(count)


j.application.stop(0)
