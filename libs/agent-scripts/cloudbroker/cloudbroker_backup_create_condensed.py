from JumpScale import j


descr = """
Follow up creation of export
"""

name = "cloudbroker_backup_create_condensed"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "io"
async = True



def action(domainid, temppath, name, storageparameters):
    import ujson, time
    from JumpScale.lib.backuptools import object_store
    from JumpScale.lib.backuptools import backup
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from CloudscalerLibcloud.utils.qcow2 import Qcow2

    connection = LibvirtUtil()
    store = object_store.ObjectStore(storageparameters['storage_type'])
    bucketname = storageparameters['bucket']
    mdbucketname = storageparameters['mdbucketname']
    domain = connection.connection.lookupByUUIDString(domainid)
    files = connection._getDomainDiskFiles(domain)
    if storageparameters['storage_type'] == 'S3':
        store.conn.connect(storageparameters['aws_access_key'], storageparameters['aws_secret_key'], storageparameters['host'], is_secure=storageparameters['is_secure'])
    else:
        #rados has config on local cpu node
        store.conn.connect()
    backupmetadata = []
    if not j.system.fs.exists(temppath):
        j.system.fs.createDir(temppath)
    for f in files:
        basefile = j.system.fs.getBaseName(f)
        tempfilepath = j.system.fs.joinPaths(temppath, basefile)
        q2 = Qcow2(f)
        q2.export(tempfilepath)
        metadata = backup.backup(store, bucketname, tempfilepath)
        j.system.fs.remove(tempfilepath)
        backupmetadata.append(metadata)
    backup.store_metadata(store, mdbucketname, name,backupmetadata)
    return {'files':backupmetadata, 'timestamp':time.time()}
