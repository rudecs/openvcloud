from JumpScale import j

descr = """
Upgrade script
Add privatenetwork field
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True

def action():
    osis_cl = j.clients.osis.getNamespace('cloudbroker')
    osis_cl.cloudspace.updateSearch({'privatenetwork': None}, {'$set': {'privatenetwork': '192.168.103.0/24'}})
