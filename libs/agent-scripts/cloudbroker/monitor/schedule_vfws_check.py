from JumpScale import j

descr = """
Schedule vfw_check
"""

organization = 'cloudscalers'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.vfw"

enable = True
async = True
log = False
period = 3600
roles = ['master',]
queue = 'process'

def action():
    import JumpScale.grid.agentcontroller
    location = j.application.config.get('cloudbroker.where_am_i')
    acl = j.clients.agentcontroller.get()
    acl.executeJumpScript('cloudscalers', 'vfws_check', role='fw', args={'location': location}, wait=False)
