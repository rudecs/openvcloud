from JumpScale import j

descr = """
Libvirt script to delete template
"""

category = "libvirt"
organization = "greenitglobe"
author = "geert@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = []
async = True


def action(ovs_connection, diskguid):
    # Delete vtemplate
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguid: guid of the template to delete
    #
    # returns None

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    path = '/vdisks/{}/delete_vtemplate'
    taskguid = ovs.post(path.format(diskguid))
    success, result = ovs.wait_for_task(taskguid)
    if not success:
        raise Exception("Could not delete template:\n{}".format(result))
