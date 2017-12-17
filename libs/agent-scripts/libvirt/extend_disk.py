from JumpScale import j

descr = """
Libvirt script to extend a disksize on ovs
"""

category = "libvirt"
organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, size, diskguid, disk_info):
    import json
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    import libvirt
    # Creates a disk from a disk template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # size: size of the disk in GB
    # diskguid: guid of the disk that needs to be used to update
    #   the volume.

    # returns true if disk was resized. False if need to restart machine in order to reflect the changes

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    # Then resize to the correct size
    path = "/vdisks/{}/extend".format(diskguid)
    res = True
    new_size = size * 1024**3
    params = dict(new_size=new_size)
    taskguid = ovs.post(path, data=json.dumps(params))
    success, result = ovs.wait_for_task(taskguid)

    if not success:
        raise Exception("Could not update disk:\n{}".format(result))

    connection = LibvirtUtil()
    domain = connection.get_domain_obj(disk_info['machineRefId'])
    if domain:
        domaindisks = list(connection.get_domain_disks(domain.XMLDesc()))
        dev = connection.get_domain_disk(disk_info['referenceId'], domaindisks)
        try:
            domain.blockResize(dev, new_size, libvirt.VIR_DOMAIN_BLOCK_RESIZE_BYTES)
        except:
            res = False

    return res
