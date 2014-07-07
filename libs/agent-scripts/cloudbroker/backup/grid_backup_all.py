from JumpScale import j

descr = """
Backup the whole grid
"""

category = "cloud"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['master']
queue = "io"
async = True
period = 3600

def action():
    import JumpScale.grid.agentcontroller
    from datetime import datetime
    now = datetime.now()
    storageparameters = {'storage_type': 'S3'}
    prefix = 'grid.backup.s3.'
    for key in  j.application.config.prefix(prefix):
        newkey = key[len(prefix):].replace('.', '_')
        storageparameters[newkey] = j.application.config.get(key)
    storageparameters['is_secure'] = storageparameters['is_secure'] == '1'

    timestamp = now.strftime("%Y%m%d-%H%M%S")

    def lxcBackup(name):
        args = {'storageparameters': storageparameters, 'name': name, 'backupname': "%s_%s" % (name, timestamp)}
        acl.executeJumpScript('cloudscalers', 'backup_lxc', args=args, role='lxchost', queue='io', wait=False)

    #daily stuff
    if now.hour == 3:
        acl = j.clients.agentcontroller.get()
        args = {'storageparameters': storageparameters}
        acl.executeJumpScript('cloudscalers', 'backup_vfws', args=args, role='master', queue='io', wait=False)
        for name in ('cloudbroker', 'gridmaster'):
            lxcBackup(name)
        if now.weekday() == 6:
            for name in ('admin', 'sentry'):
                lxcBackup(name)
