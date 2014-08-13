from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_export"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue='default'
async = True



def action(path, name, machineId,storageparameters,nid,backup_type):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import ujson, time
    from JumpScale.baselib.backuptools import object_store
    from JumpScale.baselib.backuptools import backup
    cloudbrokermodel = j.core.osis.getClientForNamespace('cloudbroker')

    vm = cloudbrokermodel.vmachine.get(machineId)
    agentcontroller = j.clients.agentcontroller.get()



    vmobject = ujson.dumps(vm.obj2dict())
    vmexport = cloudbrokermodel.vmexport.new()
    vmexport.machineId = machineId
    vmexport.type = backup_type
    vmexport.config = vmobject
    vmexport.name = name
    vmexport.timestamp = int(time.time())
    firstdisk = cloudbrokermodel.disk.get(vm.disks[0])
    vmexport.original_size = firstdisk.sizeMax
    TEMPSTORE = '/mnt/vmstor2/backups_temp'

    vmexport.status = 'CREATING'
    vmexport.bucket = storageparameters['bucket']


    if storageparameters['storage_type'] == 'S3':
        vmexport.server = storageparameters['host']
    vmexport.storagetype = storageparameters['storage_type']
    export_id = cloudbrokermodel.vmexport.set(vmexport)[0]


    if backup_type == 'raw':
        args = {'path':path, 'name':name, 'storageparameters': storageparameters}
        result = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_backup_create_raw', args=args, nid=nid, timeout=3600, wait=True)
    elif backup_type == 'condensed':
        args = {'domainid': vm.referenceId, 'temppath': TEMPSTORE, 'name':name, 'storageparameters': storageparameters}
        result = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_backup_create_condensed', args=args, nid=nid, timeout=3600, wait=True)
    else:
        raise 'Incorrect backup type'


    #save config in model

    vmexport = cloudbrokermodel.vmexport.get(export_id)

    if result['state'] == 'ERROR':
        vmexport.status = 'ERROR'
        cloudbrokermodel.vmexport.set(vmexport)
    else:
        result = result['result']
        if 'size' in result:
            vmexport.size = result['size']
        vmexport.timestamp = int(result['timestamp'])
        vmexport.files = ujson.dumps(result['files'])
        vmexport.status = 'CREATED'
        cloudbrokermodel.vmexport.set(vmexport)

    return export_id
