from JumpScale import j
import JumpScale.portal

def getClient(ip):
    port = j.application.config.get('vncproxy.libcloud.actor.port')
    key = j.application.config.get('vncproxy.libcloud.actor.secret')
    cl = j.core.portal.getClient(ip, port, key)
    return cl.getActor('libcloud','libvirt')
