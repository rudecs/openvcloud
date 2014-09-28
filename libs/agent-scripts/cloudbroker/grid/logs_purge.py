from JumpScale import j

descr = """
Purges logs
"""

name = "logs_purge"
category = "cloudbroker"
organization = "cloudscalers"
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['admin']
queue = "io"

def action(age):
    import JumpScale.baselib.elasticsearch
    start = j.base.time.getEpochAgo(age)
    esclient = j.clients.elasticsearch.get()
    query = {'range': {'epoch': {'gt': start}}}
    index='system_log'
    result = esclient.delete_by_query(index=index, query=query, doc_type='json')
    return result['ok']