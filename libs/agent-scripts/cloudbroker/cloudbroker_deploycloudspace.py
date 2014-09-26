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

    cl = j.core.portal.getClientByInstance('cloudbroker') 
    cloudspaceapi = cl.getActor('cloudapi','cloudspaces')

    return cloudspaceapi.deploy(cloudspaceId)

