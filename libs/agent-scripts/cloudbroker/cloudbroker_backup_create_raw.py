from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_backup_create_raw"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "io"
async = True



def action(path, name, storageparameters):
    import ujson, time
    from JumpScale.baselib.backuptools import object_store
    from JumpScale.baselib.backuptools import backup


    files = j.system.fs.listFilesInDir(path)
    store = object_store.ObjectStore(storageparameters['storage_type'])
    bucketname = storageparameters['bucket']
    mdbucketname = storageparameters['mdbucketname']
    if storageparameters['storage_type'] == 'S3':
        store.conn.connect(storageparameters['aws_access_key'], storageparameters['aws_secret_key'], storageparameters['host'], is_secure=storageparameters['is_secure'])
    else:
        #rados has config on local cpu node
        store.conn.connect()
    backupmetadata = []
    for f in files:
        metadata = backup.backup(store, bucketname, f)
        backupmetadata.append(metadata)
    
    backup.store_metadata(store, mdbucketname, name,backupmetadata)
    return {'files':backupmetadata, 'timestamp':time.time()}
