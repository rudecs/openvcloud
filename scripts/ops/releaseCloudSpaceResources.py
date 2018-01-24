#!/usr/bin/env python
from JumpScale import j
import JumpScale.portal
from JumpScale.baselib.cmdutils import ArgumentParser



import cloudbrokerlib.network



def _release_resources(cloudspaceId):
        
        
    whereami = j.application.config.get('cloudbroker.where_am_i')
    cbcl = j.clients.osis.getNamespace('cloudbroker')
    libvirt_actor = j.apps.libcloud.libvirt
    gridid = j.application.config.get('grid.id')
    netmgr = j.apps.jumpscale.netmgr
    network = cloudbrokerlib.network.Network(cbcl)
    cloudspace = cbcl.cloudspace.get(cloudspaceId)
    if (cloudspace.location != whereami):
        print "ERROR: Cloudspace location is %s while this is %s" % (cloudspace.location,whereami)
        return
    # delete routeros
    fws = netmgr.fw_list(gridid, str(cloudspace.id))
    if fws:
        netmgr.fw_delete(fws[0]['guid'])
    if cloudspace.networkId:
        libvirt_actor.releaseNetworkId(cloudspace.networkId)
    if cloudspace.publicipaddress:
        network.releasePublicIpAddress(cloudspace.publicipaddress)
    cloudspace.networkId = None
    cloudspace.publicipaddress = None
    cloudspace.status = 'VIRTUAL'
    cbcl.cloudspace.set(cloudspace)



if __name__ == '__main__':
    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9999))
    secret = portalcfg.get('secret')
    parser = ArgumentParser()
    parser.add_argument("-c", "--cloudspaceid")
    opts = parser.parse_args()

    cl = j.clients.portal.get('127.0.0.1', port, secret)
    
    cl.getActor('libcloud','libvirt')
    cl.getActor('jumpscale','netmgr')
    _release_resources(opts.cloudspaceid)