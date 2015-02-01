from JumpScale import j
import JumpScale.portal

def getClient(portalclient):
    cl = j.clients.portal.getByInstance(portalclient)
    return cl.getActor('libcloud','libvirt')
