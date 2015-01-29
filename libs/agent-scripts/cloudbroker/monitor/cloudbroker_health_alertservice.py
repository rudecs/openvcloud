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
    state = {}
    try:
        pdef = j.tools.startupmanager.getProcessDef('jumpscale', 'alerter')
        state['alerter'] = pdef.isRunning()
    except ProcessNotFoundException:
        state['alerter'] = False

    rediscl = j.clients.redis.getByInstance('system')
    if rediscl.hexists('healthcheck:monitoring', 'lastcheck'):
        lastchecked = j.basetype.float.fromString(rediscl.hget('healthcheck:monitoring', 'lastcheck'))
        if lastchecked < (j.base.time.getTimeEpoch() - j.base.time.getDeltaTime('15m')):
            state['healthcheck'] = False
        else:
            state['healthcheck'] = True
    else:
        state['healthcheck'] = False

    return state

if __name__ == '__main__':
   print action()