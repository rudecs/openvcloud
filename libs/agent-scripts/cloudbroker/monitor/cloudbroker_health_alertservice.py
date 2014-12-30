from JumpScale import j

descr = """
check status of alertservice
"""

organization = 'cloudscalers'
name = 'health_alertservice'
author = "martinsc@mothership1.com"
version = "1.0"
category = "cloudbroker"

enable = True
async = False
log = False

def action():
    from JumpScale.baselib.startupmanager.StartupManager import ProcessNotFoundException
    try:
        pdef = j.tools.startupmanager.getProcessDef('jumpscale', 'alerter')
    except ProcessNotFoundException:
        return False
    return pdef.isRunning()

if __name__ == '__main__':
   print action()
