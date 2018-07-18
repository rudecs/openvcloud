from JumpScale import j


descr = """
Permanently removes deleted accounts when all related resources are cleaned up. (Empties the trash can)
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "ali.chaddad@gig.tech"
license = "bsd"
version = "1.0"
roles = ['master']
queue = "hypervisor"
async = True
log = True
enable = True
period = 3600
timeout = 900

def action():
    ccl = j.clients.osis.getNamespace('cloudbroker')
    accounts = ccl.account.search({'status': 'DELETED'}, size=0)[1:]
    for account in accounts:
        acc_id = account['id']
        images = ccl.image.count({'status': 'DELETED', 'accountId': acc_id})
        cloudspaces = ccl.cloudspace.count({'status': 'DELETED', 'accountId': acc_id})
        if not cloudspaces and not images:
            ccl.account.updateSearch({'id': acc_id}, {'$set': {'status': 'DESTROYED'}})
        




if __name__ == '__main__':
    action()
