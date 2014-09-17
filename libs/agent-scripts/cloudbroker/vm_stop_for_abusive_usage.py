from JumpScale import j

descr = """
Stops a vmachine if it's abusing node's resources, and moves it to slower storage
"""

name = "vm_stop_for_abusive_usage"
category = "cloudbroker"
organization = "cloudscalers"
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['compute']
queue = "hypervisor"

def action(machineId, accountName, reason):
    # create a ticket
    from CloudscalerLibcloud import whmcs
    clientId = accountName
    departmentId = 'support'
    subject = 'Stopping vmachine "%s" for abusive resources usage' % machineId
    msg = 'Account Name: %s\nMachine ID: %s\nReason: %s' % (accountName, machineId, reason)
    priority = 1
    ticketId = whmcs.whmcstickets.create_ticket(clientId, departmentId, subject, msg, priority)

    # shutdown the vmachine
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    connection.shutdown(machineId)

    # move the vmachine to slower storage
    cmd = 'cd /mnt/vmstor; VM=vm-%s; tar cf - $VM | tar xvf - -C /mnt/vmstor2 && rm -rf $VM && ln -s /mnt/vmstor2/${VM}' % machineId
    j.system.process.execute(cmd)

    # if all went well, close the ticket
    whmcs.whmcstickets.update_ticket(ticketId, departmentId, subject, priority,
                                     'Closed', None, None, None, None) # TODO revisit
