from JumpScale import j
import JumpScale.portal

def getClient(ip):
    cl = j.core.portal.getClient(ip, 9999, '1234')
    return cl.getActor('libcloud','libvirt')
