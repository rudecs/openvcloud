from JumpScale import j

descr = """
Follow up creation of cloudspace routeros image
"""

name = "cloudbroker_accountcreate"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
queue = "hypervisor"
async = True



def action(accountid, password, email, now, portalurl, token, username, user):
    import JumpScale.grid.osis
    import JumpScale.portal



    cl = j.core.osis.getClientForNamespace('cloudbroker')
    cs = cl.cloudspace.get(cloudspaceId)
    if cs.status != 'VIRTUAL':
        return

    libvirt_actor = None #TODO
    netmgr = None #TODO
        
    #TODO: check location
    cs.status = 'DEPLOYING'
    cl.models.cloudspace.set(cs)
    networkid = cs.networkId
        
    publicipaddress = self.cb.extensions.imp.getPublicIpAddress(networkid)
    if not publicipaddress:
        libvirt_actor.releaseNetworkId(networkid)
        raise RuntimeError("Failed to get publicip for networkid %s" % networkid)
    
    cs.publicipaddress = publicipaddress
    #TODO: autogenerate long password
    password = "mqewr987BBkk#mklm)plkmndf3236SxcbUiyrWgjmnbczUJjj"
    try:
        netmgr.fw_create(str(cloudspaceId), 'admin', password, publicipaddress, 'routeros', networkid)
    except:
        libvirt_actor.releaseNetworkId(networkid)
        raise
        
    cs.status = 'DEPLOYED'
    cl.cloudspace.set(cs)


