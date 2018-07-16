from JumpScale import j

descr = """
Upgrade script
Updates ROS configuration.
"""

category = "libvirt"
organization = "greenitglobe"
author = "ali.chaddad@gig.tech"
license = "bsd"
version = "2.0"
roles = ['controller']
async = True

def action():
    vcl = j.clients.osis.getNamespace('vfw')
    vfws = vcl.virtualfirewall.search({}, size=0)[1:]
    for vfw in vfws:
        router = j.clients.routeros.get(vfw['host'], vfw['username'], vfw['password'])
        router.do("/system/hardware/set", {"multi-cpu": "no"})
        router.close()
