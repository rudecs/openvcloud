from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from JumpScale.portal.portal import exceptions
from cloudbrokerlib import authenticator
from cloudbrokerlib.baseactor import BaseActor
from JumpScale.portal.portal import exceptions
import netaddr


class cloudapi_portforwarding(BaseActor):

    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/

    """

    def __init__(self):
        super(cloudapi_portforwarding, self).__init__()
        self.netmgr = j.apps.jumpscale.netmgr

    def _getLocalIp(self, machine):
        for nic in  machine['interfaces']:
            if nic.ipAddress != 'Undefined':
                return nic.ipAddress
        return None

    @authenticator.auth(acl='C')
    @audit()
    def create(self, cloudspaceid, publicIp, publicPort, vmid, localPort, protocol=None, **kwargs):
        """
        Create a portforwarding rule
        param:cloudspaceid id of the cloudspace
        param:publicIp public ipaddress
        param:publicPort public port
        param:vmid id of the vm
        param:localPort private port
        """
        vmid = int(vmid)
        cloudspaceid = int(cloudspaceid)
        cloudspace = self.models.cloudspace.get(cloudspaceid)
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceid)
        if len(fw) == 0:
            raise exceptions.NotFound('Incorrect cloudspace or there is no corresponding gateway')
        fw_id = fw[0]['guid']
        grid_id = fw[0]['gid']

        try:
            publicIp = str(netaddr.IPNetwork(publicIp).ip)
        except netaddr.AddrFormatError:
            raise exceptions.BadRequest("Invalid public IP %s" % publicIp)

        machine = j.apps.cloudapi.machines.get(vmid)
        localIp = self._getLocalIp(machine)
        if localIp is None:
            raise exceptions.NotFound('No correct ipaddress found for this machine')

        if self._selfcheckduplicate(fw_id, publicIp, publicPort, localIp, localPort, protocol, cloudspace.gid):
            raise exceptions.Conflict("Forward to %s with port %s already exists" % (publicIp, publicPort))
        try:
            result = self.netmgr.fw_forward_create(fw_id, grid_id, publicIp, publicPort, localIp, localPort, protocol)
        except:
            raise exceptions.ServiceUnavailable("Forward to %s with port %s failed to create." % (publicIp, publicPort))
        return result


    def deleteByVM(self, machine, **kwargs):
        def getIP():
            for nic in machine.nics:
                if nic.ipAddress != 'Undefined':
                    return nic.ipAddress
            return None
        localIp = getIP()
        if localIp is None:
            return True
        cloudspaceid = machine.cloudspaceId
        cloudspace = self.models.cloudspace.get(cloudspaceid)
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceid)
        if not fw:
            return True
        fw_id = fw[0]['guid']
        grid_id = fw[0]['gid']
        forwards = self.netmgr.fw_forward_list(fw_id, grid_id)
        for fw in forwards:
            if fw['localIp'] == localIp:
                self._deleteByPort(cloudspaceid, fw['publicIp'], fw['publicPort'], fw['protocol'])
        return True

    def _selfcheckduplicate(self, fw_id, publicIp, publicPort, localIp, localPort, protocol, gid):
        forwards = self.netmgr.fw_forward_list(fw_id, gid)
        for fw in forwards:
            if fw['publicIp'] == publicIp \
               and fw['publicPort'] == publicPort \
               and fw['protocol'] == protocol:
                return True
        return False

    def _getFirewallId(self, cloudspaceId):
        cloudspace = self.models.cloudspace.get(cloudspaceId)
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceId)
        if len(fw) == 0:
            raise exceptions.NotFound('Incorrect cloudspace or there is no corresponding gateway')

        return fw[0]['guid'], fw[0]['gid']

    @authenticator.auth(acl='D')
    @audit()
    def delete(self, cloudspaceid, id, **kwargs):
        """
        Delete a specific portforwarding rule
        param:cloudspaceid if of the cloudspace
        param:id of the portforward

        """
        try:
            result = self._delete(int(cloudspaceid), id)
        except exceptions.BaseError:
            raise
        except:
            raise exceptions.ServiceUnavailable('Failed to remove Portforwarding')
        return result

    def _delete(self, cloudspaceid, id, **kwargs):
        fw_id, fw_gid = self._getFirewallId(cloudspaceid)
        forwards = self.netmgr.fw_forward_list(fw_id, fw_gid)
        id = int(id)
        if not id < len(forwards):
            raise exceptions.NotFound('Cannot find the rule with id %s' % str(id))
        forward = forwards[id]
        self.netmgr.fw_forward_delete(fw_id, fw_gid, forward['publicIp'], forward['publicPort'], forward['localIp'], forward['localPort'])
        forwards = self.netmgr.fw_forward_list(fw_id, fw_gid)
        return self._process_list(forwards, cloudspaceid)

    @authenticator.auth(acl='D')
    @audit()
    def deleteByPort(self, cloudspaceid, publicIp, publicPort, proto=None, **kwargs):
        """
        Delete a specific portforwarding rule
        param:cloudspaceid if of the cloudspace
        param:id of the portforward
        """
        try:
            result = self._deleteByPort(int(cloudspaceid), publicIp, publicPort, proto)
        except exceptions.BaseError:
            raise
        except:
            raise exceptions.ServiceUnavailable('Failed to remove Portforwarding')
        return result

    def _deleteByPort(self, cloudspaceid, publicIp, publicPort, proto, **kwargs):
        fw_id, fw_gid = self._getFirewallId(cloudspaceid)
        if not self.netmgr.fw_forward_delete(fw_id, fw_gid, publicIp, publicPort,proto):
            raise exceptions.NotFound("Could not find port forwarding with %s:%s %s" % (publicIp, publicPort, proto))
        forwards = self.netmgr.fw_forward_list(fw_id, fw_gid)
        return self._process_list(forwards, cloudspaceid)

    @authenticator.auth(acl='C')
    @audit()
    def update(self, cloudspaceid, id, publicIp, publicPort, vmid, localPort, protocol, **kwargs):
        vmid = int(vmid)
        cloudspaceid = int(cloudspaceid)
        cloudspace = self.models.cloudspace.get(cloudspaceid)
        ctx = kwargs['ctx']
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceid)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']

        forwards = self.netmgr.fw_forward_list(fw_id, cloudspace.gid)
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
        if self._selfcheckduplicate(fw_id, publicIp, publicPort, localIp, localPort, protocol, cloudspace.gid):
            ctx.start_response('403 Forbidden', [])
            return "Forward for %s with port %s already exists" % (publicIp, publicPort)
        self.netmgr.fw_forward_delete(fw_id, cloudspace.gid,
                                      forward['publicIp'], forward['publicPort'], forward['localIp'], forward['localPort'], forward['protocol'])
        self.netmgr.fw_forward_create(fw_id, cloudspace.gid, publicIp, publicPort, localIp, localPort, protocol)
        forwards = self.netmgr.fw_forward_list(fw_id, cloudspace.gid)
        return self._process_list(forwards, cloudspaceid)

    def _process_list(self, forwards, cloudspaceid):
        result = list()
        query = {'cloudspaceId': cloudspaceid, 'status': {'$ne': 'DESTROYED'}}
        machines = self.models.vmachine.search(query)[1:]
        def getMachineByIP(ip):
            for machine in machines:
                for nic in machine['nics']:
                    if nic['ipAddress'] == ip:
                        return machine

        for index, f in enumerate(forwards):
            f['id'] = index
            machine = getMachineByIP(f['localIp'])
            if machine is None:
                f['vmName'] = f['localIp']
            else:
                f['vmName'] = "%s (%s)" % (machine['name'], f['localIp'])
                f['vmid'] = machine['id']
            if not f['protocol']:
                f['protocol'] = 'tcp'
            result.append(f)
        return result

    @authenticator.auth(acl='R')
    @audit()
    def list(self, cloudspaceid, machineId=None, **kwargs):
        """
        list all portforwarding rules.
        param:cloudspaceid id of the cloudspace
        """
        machine = None
        if machineId:
            machineId = int(machineId)
            machine = self.models.vmachine.get(machineId)
        def getIP():
            if machine:
                for nic in machine.nics:
                    if nic.ipAddress != 'Undefined':
                        return nic.ipAddress
            return None
        localip = getIP()
        ctx = kwargs['ctx']
        cloudspaceid = int(cloudspaceid)
        cloudspace = self.models.cloudspace.get(cloudspaceid)
        fw = self.netmgr.fw_list(cloudspace.gid, cloudspaceid)
        if len(fw) == 0:
            ctx.start_response('404 Not Found', [])
            return 'Incorrect cloudspace or there is no corresponding gateway'
        fw_id = fw[0]['guid']
        fw_gid = fw[0]['gid']
        forwards = self.netmgr.fw_forward_list(fw_id, fw_gid, localip)
        return self._process_list(forwards, cloudspaceid)

    @authenticator.auth(acl='R')
    @audit()
    def listcommonports(self, **kwargs):
        """
        List a range of predifined ports
        """
        return [{'name': 'http', 'port': 80, 'protocol': 'tcp'},
                {'name': 'ftp', 'port': 21, 'protocol': 'tcp'},
                {'name': 'ssh', 'port': 22, 'protocol': 'tcp'}]
