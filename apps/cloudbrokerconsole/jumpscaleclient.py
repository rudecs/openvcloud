from JumpScale import j
import JumpScale.portal

def getClient(ip):
    cl = j.core.portal.getPortalClient(ip, 80, '1234')
    return cl.getActor('cloudapi','machines')
