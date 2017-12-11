from JumpScale import j

descr = """
Upgrade script
Will update all allowedVMSizes of a cloudspace that were NULL to an empty list
"""

category = "libvirt"
organization = "greenitglobe"
author = "chaddada@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True

def action():
    osis_cl = j.clients.osis.getNamespace('cloudbroker')
    scl = j.clients.osis.getNamespace('system')
    osis_cl.cloudspace.updateSearch({'allowedVMSizes': None}, {'$set': {'allowedVMSizes': []}})
    osis_cl.externalnetwork.updateSearch({'pingips': {'$in': [None, []]}}, {'$set': {'pingips': ['8.8.8.8']}})
    if scl.group.exists('finance'):
        scl.group.delete('finance')
