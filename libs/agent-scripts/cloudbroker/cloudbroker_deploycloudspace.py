from JumpScale import j

descr = """
Follow up creation of cloudspace routeros image
"""

name = "cloudbroker_deploycloudspace"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
queue = "hypervisor"
async = True



def action(cloudspaceId):
    import JumpScale.grid.osis
    import JumpScale.portal

    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9999))
    secret = portalcfg.get('secret')
    cl = j.core.portal.getClient('127.0.0.1', port, secret)
    cloudspaceapi = cl.getActor('cloudapi','cloudspaces')

    return cloudspaceapi.deploy(cloudspaceId)

