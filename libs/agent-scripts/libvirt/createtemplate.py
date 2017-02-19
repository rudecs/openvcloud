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


def action(ovs_connection, diskguid):
    # Creates sets vdisk as a template
    #
    # ovs_connection: dict holding connection info for ovs restapi
    #   eg: { ips: ['ip1', 'ip2', 'ip3'], client_id: 'dsfgfs', client_secret: 'sadfafsdf'}
    # diskguid: disk of which we are creating a template
    #
    # returns diskguid of the created template

    ovs = j.clients.openvstorage.get(ips=ovs_connection['ips'],
                                     credentials=(ovs_connection['client_id'],
                                                  ovs_connection['client_secret']))

    # Set the clone as templatename
    path = '/vdisks/{}/set_as_template'.format(diskguid)
    taskguid = ovs.post(path)
    success, result = ovs.wait_for_task(taskguid)
    if not success:
        raise Exception("Could not disk as template:\n{}".format(result))

    return diskguid
