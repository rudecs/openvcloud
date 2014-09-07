from JumpScale import j
import JumpScale.portal

def getClient(portalclient):
    cl = j.core.portal.getClientByInstance(portalclient)
    return cl.getActor('libcloud','libvirt')
