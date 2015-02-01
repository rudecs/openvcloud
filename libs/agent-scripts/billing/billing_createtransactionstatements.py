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
roles = ['billing']
queue = "io"
async = True
period = 3600 * 2 # 2 hrs



def action():
    import JumpScale.grid.osis
    import JumpScale.portal

    cl = j.clients.portal.getByInstance('cloudbroker')
    cloudspaceapi = cl.getActor('billingengine','billingengine')

    cbcl = j.clients.osis.getForNamespace('cloudbroker')
    accountIds = cbcl.account.list()
    for accountId in accountIds:
        cloudspaceapi.createTransactionStaments(accountId)

if __name__ == '__main__':
    action()
