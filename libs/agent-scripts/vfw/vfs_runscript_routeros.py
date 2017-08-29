from JumpScale import j

descr = """
Run script on routeros
"""

category = "vfw"
organization = "jumpscale"
author = "deboeckj@gig.tech"
license = "bsd"
version = "1.0"
roles = []
async = True 


def action(fwobject, script):
    host = fwobject['host']
    username = fwobject['username']
    password = fwobject['password']

    ro = j.clients.routeros.get(host, username, password)
    try:
        ro.executeScript(script)
        return True, None
    except Exception as e:
        return False, str(e)

