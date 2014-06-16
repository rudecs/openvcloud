from JumpScale import j
from cloudbrokerlib import authenticator
import ujson


class cloudapi_portforwarding(j.code.classGetBase()):

    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/

    """

    def __init__(self):

        self._te = {}
        self.actorname = "portforwarding"
        self.appname = "cloudapi"
        # cloudapi_portforwarding_osis.__init__(self)
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

    def _getLocalIp(self, machine):
        localIp = None
        if machine.nics:
            if machine.nics[0].ipAddress == 'Undefined':
                provider = self.cb.extensions.imp.getProviderByStackId(machine.stackId)
                n = self.cb.extensions.imp.Dummy(id=machine.referenceId)
                ipaddress = provider.client.ex_getIpAddress(n)
                if ipaddress:
                    machine.nics[0].ipAddress = ipaddress
                    self.models.vmachine.set(machine)
                    localIp = ipaddress
            else:
                localIp = machine.nics[0].ipAddress
        return localIp

    @authenticator.auth(acl='C')
    def create(self, cloudspaceid, publicIp, publicPort, vmid, localPort, protocol=None, **kwargs):
        """
        Create a portforwarding rule
        param:cloudspaceid id of the cloudspace
        param:publicIp public ipaddress
        param:publicPort public port
        param:vmid id of the vm
        param:localPort private port
        """
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']

        machine = self.models.vmachine.get(vmid)
        localIp = self._getLocalIp(machine)
        if not localIp:
            ctx.start_response('404 Not Found', [])
            return 'No correct ipaddress found for this machine'

        if self._selfcheckduplicate(fw_id, publicIp, publicPort, localIp, localPort, protocol):
            ctx.start_response('403 Forbidden', [])
            return "Forward to %s with port %s already exists" % (localIp, localPort)
        return self.netmgr.fw_forward_create(fw_id, self.gridid, publicIp, publicPort, localIp, localPort, protocol)

    def deleteByVM(self, machine, **kwargs):
        cloudspaceid = str(machine.cloudspaceId)
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if not fw:
            return True
        fw_id = fw[0]['guid']
        localIp = self._getLocalIp(machine)
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        for idx, fw in enumerate(forwards):
            if fw['localIp'] == localIp:
                self._delete(cloudspaceid, idx)
        return True

    def _selfcheckduplicate(self, fw_id, publicIp, publicPort, localIp, localPort, protocol):
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        for fw in forwards:
            if fw['localIp'] == localIp \
               and fw['localPort'] == localPort \
               and fw['publicIp'] == publicIp \
               and fw['publicPort'] == publicPort \
               and fw['protocol'] == protocol:
                return True
        return False

    @authenticator.auth(acl='D')
    def delete(self, cloudspaceid, id, **kwargs):
        """
        Delete a specific portforwarding rule
        param:cloudspaceid if of the cloudspace
        param:id of the portforward

        """
        ctx = kwargs['ctx']
        result = self._delete(cloudspaceid, id)
        if result == -1:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        elif result == -2:
            ctx.start_response('404 Not Found', [])
            return 'Cannot find the rule with id %s' % str(id)
        return result

    def _delete(self, cloudspaceid, id, **kwargs):
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw) == 0:
            return -1
        fw_id = fw[0]['guid']
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        id = int(id)
        if not id < len(forwards):
            return -2
        forward = forwards[id]
        self.netmgr.fw_forward_delete(fw_id, self.gridid, forward['publicIp'], forward['publicPort'], forward['localIp'], forward['localPort'])
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        return self._process_list(forwards)

    @authenticator.auth(acl='C')
    def update(self, cloudspaceid, id, publicIp, publicPort, vmid, localPort, protocol, **kwargs):
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']

        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        id = int(id)
        if not id < len(forwards):
            ctx.start_response('404 Not Found', [])
            return 'Cannot find the rule with id %s' % str(id)
        forward = forwards[id]
        machine = self.models.vmachine.get(vmid)
        if machine.nics:
            if machine.nics[0].ipAddress != 'Undefined':
                localIp = machine.nics[0].ipAddress
            else:
                ctx.start_response('404 Not Found', [])
                return 'No correct ipaddress found for machine with id %s' % vmid
        if self._selfcheckduplicate(fw_id, publicIp, publicPort, localIp, localPort, protocol):
            ctx.start_response('403 Forbidden', [])
            return "Forward for %s with port %s already exists" % (localIp, localPort)
        self.netmgr.fw_forward_delete(fw_id, self.gridid,
                                      forward['publicIp'], forward['publicPort'], forward['localIp'], forward['localPort'], forward['protocol'])
        self.netmgr.fw_forward_create(fw_id, self.gridid, publicIp, publicPort, localIp, localPort, protocol)
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        return self._process_list(forwards)

    def _process_list(self, forwards):
        result = list()
        for index, f in enumerate(forwards):
            f['id'] = index
            query = {}
            query['query'] = {'term': {'ipAddress': f['localIp']}}
            machine = self.models.vmachine.find(ujson.dumps(query))
            if machine['total'] != 1:
                f['vmName'] = f['localIp']
            else:
                f['vmName'] = "%s (%s)" % (machine['result'][0]['_source']['name'], f['localIp'])
                f['vmid'] = machine['result'][0]['_source']['id']
            if not f['protocol']:
                f['protocol'] = 'tcp'
            result.append(f)
        return result

    @authenticator.auth(acl='R')
    def list(self, cloudspaceid, **kwargs):
        """
        list all portforwarding rules.
        param:cloudspaceid id of the cloudspace
        """
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(self.gridid, cloudspaceid)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']
        forwards = self.netmgr.fw_forward_list(fw_id, self.gridid)
        return self._process_list(forwards)

    @authenticator.auth(acl='R')
    def listcommonports(self, **kwargs):
        """
        List a range of predifined ports
        """
        return [{'name': 'http', 'port': 80, 'protocol': 'tcp'},
                {'name': 'ftp', 'port': 21, 'protocol': 'tcp'},
                {'name': 'ssh', 'port': 22, 'protocol': 'tcp'}]
