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
queue = "hypervisor"

def action(machineId, accountName, reason):
    # create a ticket
    import JumpScale.lib.whmcs
    subject = 'Stopping vmachine "%s" for abusive resources usage' % machineId
    msg = 'Account Name: %s\nMachine ID: %s\nReason: %s' % (accountName, machineId, reason)
    priority = 1
    ticketId = j.tools.whmcs.tickets.create_ticket(subject, msg, priority)

    # shutdown the vmachine
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    connection.shutdown(machineId)

    # move the vmachine to slower storage
    cmd = 'cd /mnt/vmstor; VM=vm-%s; tar cf - $VM | tar xvf - -C /mnt/vmstor2 && rm -rf $VM && ln -s /mnt/vmstor2/${VM}' % machineId
    j.system.process.execute(cmd)

    # if all went well, close the ticket
    j.tools.whmcs.tickets.close_ticket(ticketId)
