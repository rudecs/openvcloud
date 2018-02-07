from JumpScale import j
import time
descr = """
Libvirt script to create template
"""

name = "createtemplate"
category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskguid, new_vdiskguid, template_name):
    # Creates sets vdisk as a template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguid: disk of which we are creating a template
    #
    # returns diskguid of the created template
    from CloudscalerLibcloud import openvstorage
    from CloudscalerLibcloud.utils.gridconfig import GridConfig
    config = GridConfig()
    username = config.settings['ovs_credentials'].get('edgeuser', '')
    password = config.settings['ovs_credentials'].get('edgepassword','')

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))
    disk = ovs.get('/vdisks/{}'.format(diskguid))

    storage_drivers = ovs.get('/storagedrivers', params={'contents': 'storagedriver_id'})['data']
    def getDiskPath(disk):
        storagedriver_id = disk['storagedriver_id']
        for sd in storage_drivers:
            if sd['storagedriver_id'] == storagedriver_id:
                break
        storage_ip = sd['storage_ip']
        edge_port = sd['ports']['edge']
        path = 'openvstorage+tcp:{}:{}{}'.format(storage_ip, edge_port, disk['devicename'].split('.')[0])
        if username and password:
            path = '{}:username={}:password={}'.format(path, username, password)
        return path
    
    def cleanup(snapshot_guid=None, cloned_diskguid=None):
        try:
            if cloned_diskguid:
                path = '/vdisks/{}/delete'
                taskguid = ovs.post(path.format(cloned_diskguid))
                success, result = ovs.wait_for_task(taskguid)
                if not success:
                    raise Exception("Could not delete disk:\n{}".format(result))

            if snapshot_guid:
                path_delete_snapshot = '/vdisks/{}/remove_snapshot'
                taskguid = ovs.post(path_delete_snapshot.format(diskguid),
                                    params=dict(snapshot_id=snapshot_guid))
                success, result = ovs.wait_for_task(taskguid)
                if not success:
                    raise Exception("Could not delete snapshot:\n{}".format(result))
        except:
            pass
            
    # create snapshot 
    path = '/vdisks/{}/create_snapshot'
    params = dict(name=template_name, sticky=True)
    taskguid = ovs.post(path.format(diskguid), params=params)
    success, snapshot_guid = ovs.wait_for_task(taskguid)
    if not success:
        raise Exception("Could not create snapshots:\n{}".format(snapshot_guid))

    # clone the snapshot
    clone_path = '/vdisks/{}/clone'
    # Create clone
    taskguid = ovs.post(clone_path.format(diskguid),
                        params=dict(name=template_name,
                                    storagerouter_guid=disk['storagerouter_guid'],
                                    snapshot_id=snapshot_guid))
    success, result = ovs.wait_for_task(taskguid)
    if not success:
        cleanup(snapshot_guid=snapshot_guid)
        raise Exception("Could not create clone:\n{}".format(result))
    cloned_diskguid = result['vdisk_guid']
    cloned_disk = ovs.get('/vdisks/{}'.format(cloned_diskguid))
    new_disk = ovs.get('/vdisks/{}'.format(new_vdiskguid))
    src = getDiskPath(cloned_disk)
    dest = getDiskPath(new_disk)
    try:
        j.system.platform.qemu_img.convert(src, None, dest, 'raw', createTarget=False)
    except:
        cleanup(snapshot_guid=snapshot_guid, cloned_diskguid=cloned_diskguid)
        raise

    # Set the new disk as template
    path = '/vdisks/{}/set_as_template'.format(new_vdiskguid)
    taskguid = ovs.post(path)
    success, result = ovs.wait_for_task(taskguid)
    if not success:
        cleanup(snapshot_guid=snapshot_guid, cloned_diskguid=cloned_diskguid)    
        raise Exception("Could not create a template:\n{}".format(result))
    # delete the snapshot and cloned_disk
    cleanup(snapshot_guid=snapshot_guid, cloned_diskguid=cloned_diskguid)

    return dest
