from JumpScale import j
import json

class cloudbroker_health(j.code.classGetBase()):
    """
    API Check status of osis and alerter
    """
    def __init__(self):
        #self.actorname="health"
        #self.appname="cloudbroker"
	self.acl = j.clients.agentcontroller.get()
        #cloudbroker_health_osis.__init__(self)

    def status(self, **kwargs):
        """
        check status of osis and alerter
        result dict
        """
	ctx = kwargs.get('ctx')
	headers = [('Content-Type', 'application/json'), ]
	resp = {}
	try:
            dbstate = j.core.portal.active.osis.getStatus()
            resp['mongodb'] = dbstate['mongodb']
            resp['influxdb'] = dbstate['influxdb']
	except Exception:
            resp['mongodb'] = False
            resp['influxdb'] = False

	result = self.acl.executeJumpscript('cloudscalers','health_alertservice', role='master',gid=j.application.whoAmI.gid, wait=True, timeout=30)
	if result['state'] != 'OK':
            resp['alerter'] = False
	else:
            resp['alerter'] = result['result']

	if all(resp.values()):
            ctx.start_response('200 Ok',headers)
	else:
            ctx.start_response('503 Service Unavailable',headers)
	return json.dumps(resp)

