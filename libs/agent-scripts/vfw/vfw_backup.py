from JumpScale import j

descr = """
backup vfw config files
"""

organization = "jumpscale"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
category = "vfw.backup.config"
period = "3 1 * * *"
enable = True
async = True
roles = ["fw"]
queue ='io'

def action():
    import JumpScale.grid.osis
    import tarfile
    import JumpScale.baselib.mailclient

    backuppath = j.system.fs.joinPaths(j.dirs.tmpDir, 'backup', 'vfw')
    timestamp = j.base.time.getTimeEpoch()
    timestamp = j.base.time.formatTime(timestamp, "%Y%m%d_%H%M%S")
    vfwerrors = list()
    try:
        import JumpScale.lib.routeros
        if j.system.fs.exists(backuppath):
            j.system.fs.removeDirTree(backuppath)

        osiscl = j.core.osis.client
        vfwcl = j.core.osis.getClientForCategory(osiscl, 'vfw', 'virtualfirewall')

        routeros_password = j.application.config.get('vfw.admin.passwd')

        alivevfws = {'nid': j.application.whoAmI.nid, 'gid': j.application.whoAmI.gid}
        vfws = vfwcl.search(alivevfws)[1:]

        for vfw in vfws:
            try:
                routeros = j.clients.routeros.get(vfw['host'], 'vscalers', routeros_password)
                name = vfw['name'] or vfw['domain']
                path = j.system.fs.joinPaths(backuppath, name)
                routeros.backup(name, path)
            except Exception:
                vfw['pubips'] = ', '.join(vfw['pubips'])
                vfwerrors.append('ID: %(id)s      CloudSpaceId: %(domain)s      PUBLIC IP: %(pubips)s' % vfw) 


        #targz
        backupdir = j.system.fs.joinPaths(j.dirs.varDir, 'backup', 'vfw')
        j.system.fs.createDir(backupdir)
        outputpath = j.system.fs.joinPaths(backupdir, '%s.tar.gz' % timestamp)
        with tarfile.open(outputpath, "w:gz") as tar:
            tar.add(backuppath)
        j.system.fs.removeDirTree(backuppath)
    except Exception:
        import traceback
        error = traceback.format_exc()
        message = '''
VFW backup at %s failed.
Data should have been backed up to %s on the admin node.

Exception:
-----------------------------
%s
-----------------------------
    ''' % (timestamp, backuppath, error)
        j.errorconditionhandler.raiseOperationalWarning(message, 'monitoring')
    finally:
        if vfwerrors:
            message = '''
VFW backup at %s failed.
Data should have been backed up to %s on the admin node.

These vfws have failed to backup:
-----------------------------
%s
-----------------------------
        ''' % (timestamp, backuppath, '\n'.join(vfwerrors))
            j.errorconditionhandler.raiseOperationalWarning(message, 'monitoring')


if __name__ == '__main__':
    import JumpScale.grid.osis
    j.core.osis.client = j.core.osis.getClientByInstance('processmanager')
    action()
