from JumpScale import j

descr = """
Backup the whole grid
"""

category = "cloud"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
queue = "io"
async = True



def action(storageparameters):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    acl = j.clients.agentcontroller.get()
    TEMPSTORE = '/mnt/vmstor2/backups_temp'

    vcl = j.clients.osis.getForNamespace('vfw')
    for guid in vcl.virtualfirewall.list():
        vfw = vcl.virtualfirewall.get(guid)
        networkid = "%04x" % vfw.id
        name = "routeros_%s" % networkid
        files = ['/mnt/vmstor/routeros/%(id)s/routeros-small-%(id)s.qcow2' % {'id': networkid} ]
        args = {'name': name,
                'temppath': TEMPSTORE,
                'files': files,
                'storageparameters': storageparameters}

        acl.executeJumpscript('cloudscalers', 'cloudbroker_backup_create_condensed', nid=vfw.nid, gid=vfw.gid, args=args, queue='io', wait=False)
