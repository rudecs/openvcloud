from JumpScale import j

descr = """
Follow up import of export
"""

name = "cloudbroker_import"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "default"
async = True



def action(path, metadata ,storageparameters,nid):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import ujson
    agentcontroller = j.clients.agentcontroller.get()

    args = {'path':path, 'metadata':metadata, 'storageparameters': storageparameters, 'qcow_only':False, 'filename': None}

    result = agentcontroller.executeJumpscript('cloudscalers', 'cloudbroker_import_onnode', args=args, nid=nid, wait=True)['result']

    return True