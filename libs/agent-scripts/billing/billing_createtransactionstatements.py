from JumpScale import j

descr = """
Generate transaction statements for all accounts
"""

name = "billing_createtransactionstatements"
category = "cloudbroker"
organization = "cloudscalers"
author = "development@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "hypervisor"
async = True




def action():
    import JumpScale.grid.osis
    import JumpScale.portal

    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'billingengine', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9402))
    secret = portalcfg.get('secret')
    cl = j.core.portal.getClient('127.0.0.1', port, secret)
    cloudspaceapi = cl.getActor('billingengine','billingengine')

    cbcl = j.core.osis.getClientForNamespace('cloudbroker')
    accountIds = cbcl.account.list()
    for accountId in accountIds:
        cloudspaceapi.createTransactionStaments(accountId)
