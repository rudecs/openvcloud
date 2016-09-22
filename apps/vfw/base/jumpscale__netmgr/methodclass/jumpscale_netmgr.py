from JumpScale import j
from JumpScale.portal.portal import exceptions


class jumpscale_netmgr(j.code.classGetBase()):
    """
    net manager

    """
    def __init__(self):
        self.client = j.clients.osis.getByInstance('main')
        self.osisvfw = j.clients.osis.getCategory(self.client, 'vfw', 'virtualfirewall')
        self.nodeclient = j.clients.osis.getCategory(self.client, 'system', 'node')
        self.gridclient = j.clients.osis.getCategory(self.client, 'system', 'grid')
        self.agentcontroller = j.clients.agentcontroller.get()
        self.json = j.db.serializers.getSerializerType('j')
        self._ovsdata = {}

    def get_ovs_credentials(self, gid):
        cachekey = 'credentials_{}'.format(gid)
        if cachekey not in self._ovsdata:
            grid = self.gridclient.get(gid)
            credentials = grid.settings['ovs_credentials']
            self._ovsdata[cachekey] = credentials
        return self._ovsdata[cachekey]

    def get_ovs_connection(self, gid):
        cachekey = 'ovs_connection_{}'.format(gid)
        if cachekey not in self._ovsdata:
            ips = []
            addresses = self.nodeclient.search({'$query': {'roles': 'storagedriver',
                                                           'netaddr.name': 'backplane1',
                                                           'gid': gid},
                                                '$fields': ['netaddr']})[1:]
            for nodeaddresses in addresses:
                for nodeaddress in nodeaddresses['netaddr']:
                    if nodeaddress['name'] == 'backplane1':
                        ips.extend(nodeaddress['ip'])

            credentials = self.get_ovs_credentials(gid)
            connection = {'ips': ips,
                          'client_id': credentials['client_id'],
                          'client_secret': credentials['client_secret']}
            self._ovsdata[cachekey] = connection
        return self._ovsdata[cachekey]

    def _getVFWObject(self, fwid):
        try:
            fwobj = self.osisvfw.get(fwid)
        except:
            raise exceptions.ServiceUnavailable("VFW with id %s is not deployed yet!" % fwid)
        if not fwobj.nid:
            raise exceptions.ServiceUnavailable("VFW with id %s is not deployed yet!" % fwid)
        return fwobj

    def fw_create(self, gid, domain, login, password, publicip, type, networkid, publicgwip, publiccidr, **kwargs):
        """
        param:domain needs to be unique name of a domain,e.g. a group, space, ... (just to find the FW back)
        param:gid grid id
        param:nid node id
        param:masquerade do you want to allow masquerading?
        param:login admin login to the firewall
        param:password admin password to the firewall
        param:host management address to manage the firewall
        param:type type of firewall e.g routeros, ...
        """
        fwobj = self.osisvfw.new()
        fwobj.domain = domain
        fwobj.id = networkid
        fwobj.gid = gid
        fwobj.pubips.append(publicip)
        fwobj.type = type
        key = self.osisvfw.set(fwobj)[0]
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        if type == 'routeros':
            args = {'networkid': networkid,
                    'password': password,
                    'publicip': publicip,
                    'publicgwip': publicgwip,
                    'publiccidr': publiccidr,
                    }
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_create_routeros', role='fw', gid=gid, args=args, queue='default', wait=False)
            fwobj.deployment_jobguid = job['guid']
            result = self.agentcontroller.waitJumpscript(job=job)

            if result['state'] != 'OK':
                self.osisvfw.delete(key)
                args = {'ovs_connection': self.get_ovs_connection(gid), 'diskpath': '/routeros/{0:04x}/routeros-small-{0:04x}.raw'.format(fwobj.id)}

                job = self.agentcontroller.executeJumpscript('greenitglobe', 'deletedisk_by_path', role='storagedriver', gid=fwobj.gid, args=args)

                if job['state'] != 'OK':
                    raise exceptions.ServiceUnavailable("Failed to remove vfw with volume %s" % networkid)

                raise exceptions.ServiceUnavailable("Failed to create create fw for domain %s job was %s" % (domain, result['id']))
            data = result['result']
            fwobj.host = data['internalip']
            fwobj.username = data['username']
            fwobj.password = data['password']
            fwobj.nid = data['nid']
            self.osisvfw.set(fwobj)
            return result
        else:
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_create', role='fw', gid=gid, args=args, wait=False)
            fwobj.deployment_jobguid = job['guid']
            result = self.agentcontroller.waitJumpscript(job=job)
            return result

    def fw_move(self, fwid, targetNid, **kwargs):
        fwobj = self._getVFWObject(fwid)
        srcnode = self.nodeclient.get("%s_%s" % (fwobj.gid, fwobj.nid))

        def get_backplane_ip(node):
            for nicinfo in node.netaddr:
                if nicinfo['name'] == 'backplane1':
                    return nicinfo['ip'][0]
        srcip = get_backplane_ip(srcnode)
        args = {'networkid': fwobj.id,
                'sourceip': srcip}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_migrate_routeros', nid=targetNid, gid=fwobj.gid, args=args)
        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to move routeros check job %(guid)s" % job)
        fwobj.nid = targetNid
        self.osisvfw.set(fwobj)
        return True

    def fw_get_ipaddress(self, fwid, macaddress):
        fwobj = self._getVFWObject(fwid)
        args = {'fwobject': fwobj.obj2dict(), 'macaddress': macaddress}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_get_ipaddress_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to retreive IPAddress for macaddress %s. Error: %s" % (macaddress, job['result']['errormessage']))
        return job['result']

    def fw_remove_lease(self, fwid, macaddress):
        fwobj = self._getVFWObject(fwid)
        args = {'fwobject': fwobj.obj2dict(), 'macaddress': macaddress}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_remove_lease_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to release lease for macaddress %s. Error: %s" % (macaddress, job['result']['errormessage']))
        return job['result']

    def fw_set_password(self, fwid, username, password):
        fwobj = self._getVFWObject(fwid)
        args = {'fwobject': fwobj.obj2dict(), 'username': username, 'password': password}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_set_password_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to set password. Error: %s" % (job['result']['errormessage']))
        return job['result']

    def fw_get_openvpn_config(self, fwid, **kwargs):
        fwobj = self._getVFWObject(fwid)
        args = {'fwobject': fwobj.obj2dict()}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_get_openvpn_config_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to get OpenVPN Config")
        return job['result']

    def fw_delete(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        if fwobj.type == 'routeros':
            args = {'networkid': fwobj.id}
            if fwobj.nid:
                job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_destroy_routeros', nid=fwobj.nid, gid=fwobj.gid, args=args)
                if job['state'] != 'OK':
                    raise exceptions.ServiceUnavailable("Failed to remove vfw with id %s" % fwid)
                args = {'ovs_connection': self.get_ovs_connection(fwobj.gid), 'diskpath': '/routeros/{0:04x}/routeros-small-{0:04x}.raw'.format(fwobj.id)}
                job = self.agentcontroller.executeJumpscript('greenitglobe', 'deletedisk_by_path', role='storagedriver', gid=fwobj.gid, args=args)
                if job['state'] != 'OK':
                    raise exceptions.ServiceUnavailable("Failed to remove vfw with id %s" % fwid)
            self.osisvfw.delete(fwid)
        else:
            result = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_delete', nid=fwobj.nid, gid=fwobj.gid, args=args)['result']
            if result:
                self.osisvfw.delete(fwid)
            return result

    def fw_destroy(self, fwid):
        self.osisvfw.delete(fwid)

    def _applyconfig(self, gid, nid, args):
        if args['fwobject']['type'] == 'routeros':
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig_routeros', gid=gid, nid=nid, args=args)
        else:
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig', gid=gid, nid=nid, args=args)

        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable('Failed to apply config')
        return job['result']

    def fw_forward_create(self, fwid, gid, fwip, fwport, destip, destport, protocol='tcp', **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport str,,port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        with self.osisvfw.lock(fwid):
            fwobj = self._getVFWObject(fwid)
            rule = fwobj.new_tcpForwardRule()
            rule.fromAddr = fwip
            rule.fromPort = str(fwport)
            rule.toAddr = destip
            rule.toPort = str(destport)
            rule.protocol = protocol
            self.osisvfw.set(fwobj)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
        result = self._applyconfig(fwobj.gid, fwobj.nid, args)
        if not result:
            self.fw_forward_delete(fwid, gid, fwip, fwport, destip, destport, protocol, apply=False)
        return result

    def fw_forward_delete(self, fwid, gid, fwip, fwport, destip=None, destport=None, protocol=None, apply=True, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        with self.osisvfw.lock(fwid):
            fwobj = self._getVFWObject(fwid)
            change = False
            result = False
            for rule in fwobj.tcpForwardRules:
                if rule.fromAddr == fwip and rule.fromPort == str(fwport):
                    if protocol and rule.protocol and rule.protocol.lower() != protocol.lower():
                        continue
                    change = True
                    fwobj.tcpForwardRules.remove(rule)
            if change:
                self.osisvfw.set(fwobj)
        if change and apply:
            args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
            result = self._applyconfig(fwobj.gid, fwobj.nid, args)
        return result

    def fw_forward_list(self, fwid, gid, localip=None, **kwargs):
        """
        list all portformarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        result = list()
        if localip:
            for rule in fwobj.tcpForwardRules:
                if localip == rule.toAddr:
                    result.append({'publicIp': rule.fromAddr,
                                   'publicPort': rule.fromPort,
                                   'localIp': rule.toAddr,
                                   'localPort': rule.toPort,
                                   'protocol': rule.protocol})
        else:
            for rule in fwobj.tcpForwardRules:
                result.append({'publicIp': rule.fromAddr,
                               'publicPort': rule.fromPort,
                               'localIp': rule.toAddr,
                               'localPort': rule.toPort,
                               'protocol': rule.protocol})
        return result

    def fw_list(self, gid, domain=None, **kwargs):
        """
        param:gid grid id
        param:domain if not specified then all domains
        """
        result = list()
        filter = dict()
        if domain:
            filter['domain'] = str(domain)
        if gid:
            filter['gid'] = gid
        fields = ('domain', 'name', 'gid', 'nid', 'guid')
        vfws = self.osisvfw.search(filter)[1:]
        for vfw in vfws:
            vfwdict = {}
            for field in fields:
                vfwdict[field] = vfw.get(field)
            result.append(vfwdict)
        return result

    def fw_start(self, fwid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self._getVFWObject(fwid)
        args = {'networkid': fwobj.id}
        if fwobj.type == 'routeros':
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_start_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        else:
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_start', gid=fwobj.gid, nid=fwobj.nid, args=args)

        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to start vfw")
        return job['result']

    def fw_stop(self, fwid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self._getVFWObject(fwid)
        args = {'networkid': fwobj.id}
        if fwobj.type == 'routeros':
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_stop_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        else:
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_stop', gid=fwobj.gid, nid=fwobj.nid, args=args)

        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to start vfw")
        return job['result']

    def fw_check(self, fwid, **kwargs):
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self._getVFWObject(fwid)
        args = {'networkid': fwobj.id}
        if fwobj.type == 'routeros':
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_checkstatus_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        else:
            job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_checkstatus', gid=fwobj.gid, nid=fwobj.nid, args=args)

        if job['state'] != 'OK':
            raise exceptions.ServiceUnavailable("Failed to get vfw status")
        return job['result']
