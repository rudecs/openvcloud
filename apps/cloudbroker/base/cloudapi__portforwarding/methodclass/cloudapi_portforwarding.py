from JumpScale import j
import ujson
class cloudapi_portforwarding(j.code.classGetBase()):
    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/
    
    """
    def __init__(self):
        
        self._te={}
        self.actorname="portforwarding"
        self.appname="cloudapi"
        #cloudapi_portforwarding_osis.__init__(self)
        self._cb = None
        self._models = None
        self.netmgr = j.apps.jumpscale.netmgr
        self.gridid = j.application.config.get('grid.id')
        pass

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

    def create(self, cloudspaceid, publicIp, publicPort, vmName, privatePort, **kwargs):
        """
        Create a portforwarding rule
        param:cloudspaceid id of the cloudspace
        param:publicIp public ipaddress
        param:publicPort public port
        param:vmName name of the vm
        param:privatePort private port
        """
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw)  == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway' 
        fw_id = fw[0]['guid']
        query = {}
        query['query'] = {'term': {'name':vmName,'cloudspaceId':cloudspaceid}}
        machine = self.models.vmachine.find(ujson.dumps(query))
        if machine['total'] != 1:
            ctx.start_response('404 Not Found', [])
            return 'No machine with name %s found in cloudspace' % vmName
        else:
            m = machine['result'][0]['_source']
            if machine.nics:
                if machine.nics[0].ipaddress != 'Undefined':
                    privateIp = machine.nics[0].ipaddress
                else:
                    ctx.start_response('404 Not Found', [])
                    return 'No correct ipaddress found for machine with name %s' % vmName
        return self.netmgr.fw_forward_create(fw_id, self.gridid, publicIp, publicPort, privateIp, privatePort)

    
    def delete(self, cloudspaceid, id, **kwargs):
        """
        Delete a specific portforwarding rule
        param:cloudspaceid if of the cloudspace
        param:id of the portforward
  
        """
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw)  == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        id = int(id)
        if not id < len(forwards):
            ctx.start_response('404 Not Found', [])
            return 'Cannot find the rule with id %s' % str(id)
        forward = forwards[id]
        self.netmgr.fw_forward_delete(fw_id, self.gridid, forward['publicIp'], forward['publicPort'], forward['localIp'], forward['localPort'])
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        return self._process_list(forwards)

    def _process_list(self, forwards):
        index = 0
        result = list()
        for f in forwards:
            f['id'] = index
            query = {}
            query['query'] = {'term': {'ipAddress':f['localIp']}}
            machine = self.models.vmachine.find(ujson.dumps(query))
            if machine['total'] != 1:
                f['vmName'] = f['localIp']
            else:
                f['vmName'] = "%s (%s)" % (machine['result'][0]['_source']['name'], f['localIp'])
            result.append(f)
            index = index + 1
        return result
    
    def list(self, cloudspaceid, **kwargs):
        """
        list all portforwarding rules.
        param:cloudspaceid id of the cloudspace
        """
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw)  == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        return self._process_list(forwards)
     

    def listcommonports(self, **kwargs):
        """
        List a range of predifined ports
        """
        return [{'name':'http','port':80}, {'name':'ftp', 'port': 21}, {'name':'ssh', 'port': 22 }]




    
