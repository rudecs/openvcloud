from JumpScale import j

descr = """
Applies the rules in the passed fwobject to the given LXC machine name
"""

name = "vfs_applyconfig_routeros"
category = "vfw"
organization = "jumpscale"
author = "hendrik@incubaid.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(name, fwobject):
    host = fwobject['host']
    username = fwobject['username']
    password = fwobject['password']

    if not j.system.net.waitConnectionTest(host, 8728, timeout=30):
        raise RuntimeError("Failed to get connection to api")
    ro = j.clients.routeros.get(host, username, password)
    neededrules = set()
    existingrules = set()
    for rule in fwobject['tcpForwardRules']:
        protocol = rule.get('protocol', 'tcp')
        neededrules.add((rule['fromAddr'], rule['fromPort'], rule['toAddr'], rule['toPort'], protocol))
    for rule in ro.listPortForwardRules('cloudbroker'):
        existingrules.add((rule['dst-address'], rule['dst-port'], rule['to-addresses'], rule['to-ports'], rule['protocol']))
    
    newrules = neededrules - existingrules
    for rule in newrules:
        ro.addPortForwardRule(rule[0], rule[1], rule[2], rule[3], tags='cloudbroker', protocol=rule[4])
    rulestodelete = existingrules - neededrules
    for rule in rulestodelete:
        ro.deletePortForwardRule(rule[0], rule[1])
    leases = fwobject.get('leases')
    if leases:
        ro.add_leases(leases)
    return True
