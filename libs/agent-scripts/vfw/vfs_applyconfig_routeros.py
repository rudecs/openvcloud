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
    ro.deletePortForwardRules(tags='cloudbroker')
    for rule in fwobject['tcpForwardRules']:
        protocol = rule.get('protocol', 'tcp')
        ro.addPortForwardRule(rule['fromAddr'], rule['fromPort'], rule['toAddr'], rule['toPort'], tags='cloudbroker', protocol=protocol)
    leases = fwobject.get('leases')
    if leases:
        ro.add_leases(leases)
    return True
