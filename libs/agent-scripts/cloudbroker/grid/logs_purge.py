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
roles = ['master']
queue = "io"

def action(age, gid=None):
    try:
        start = j.base.time.getEpochAgo(age)
    except Exception:
        return False
    import JumpScale.grid.osis
    syscl = j.clients.osis.getForNamespace('system')
    query = {'epoch':{'$lt':start}}
    if gid:
        query['gid'] = int(gid)
    result = syscl.log.deleteSearch(query)
    return result