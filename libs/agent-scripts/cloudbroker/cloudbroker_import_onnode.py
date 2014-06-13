from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_import_onnode"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "io"
async = True



def action(path, metadata ,storageparameters):
    import ujson, time
    from JumpScale.baselib.backuptools import object_store
    from JumpScale.baselib.backuptools import backup
    

    store = object_store.ObjectStore(storageparameters['storage_type'])
    bucketname = storageparameters['bucket']
    j.system.fs.createDir(path)
    if storageparameters['storage_type'] == 'S3':
        store.conn.connect(storageparameters['aws_access_key'], storageparameters['aws_secret_key'], storageparameters['host'], is_secure=storageparameters['is_secure'])
    else:
        #rados has config on local cpu node
        store.conn.connect()
    for f in metadata:
        filepath = j.system.fs.getBaseName(f['path'])
        restorepath = j.system.fs.joinPaths(path, filepath)
        if j.system.fs.exists(restorepath):
            raise Exception('%s already exists' % restorepath)
        restore = backup.restore(store, bucketname, restorepath, f['fileparts'])
    return restorepath

