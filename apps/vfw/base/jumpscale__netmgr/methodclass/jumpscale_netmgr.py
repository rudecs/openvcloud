from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.lib.lxc
import JumpScale.baselib.serializers

class jumpscale_netmgr(j.code.classGetBase()):
    """
    net manager

    """
    def __init__(self):

        self._te = {}
        self.actorname = "netmgr"
        self.appname = "jumpscale"
        #jumpscale_netmgr_osis.__init__(self)
        self.client = j.core.osis.getClientByInstance('main')
        self.osisvfw = j.core.osis.getClientForCategory(self.client, 'vfw', 'virtualfirewall')
        self.nodeclient = j.core.osis.getClientForCategory(self.client, 'system', 'node')
        self.agentcontroller = j.clients.agentcontroller.get()
        self.json = j.db.serializers.getSerializerType('j')

    def fw_check(self, fwid, gid, **kwargs):
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        return self.agentcontroller.executeJumpscript('jumpscale', 'vfs_checkstatus', nid=fwobj.nid, gid=fwobj.gid, args=args)['result']

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
        fwobj.type =  type
        key = self.osisvfw.set(fwobj)[0]
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name)}
        if type == 'routeros':
            args = {'networkid': networkid,
                    'password': password,
                    'publicip': publicip,
                    'publicgwip': publicgwip,
                    'publiccidr': publiccidr,
                    }
            result = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_create_routeros', role='fw', gid=gid, args=args, queue='hypervisor')
            if result['state'] != 'OK':
                self.osisvfw.delete(key)
                raise RuntimeError("Failed to create create fw for domain %s job was %s" % (domain, result['id']))
            data = result['result']
            fwobj.host = data['internalip']
            fwobj.username = data['username']
            fwobj.password = data['password']
            fwobj.nid = data['nid']
            self.osisvfw.set(fwobj)
        else:
            return self.agentcontroller.executeJumpscript('jumpscale', 'vfs_create', role='fw', gid=gid, args=args)['result']

    def fw_move(self, fwid, targetNid, **kwargs):
        fwobj = self.osisvfw.get(fwid)
        srcnode = self.nodeclient.get("%s_%s" % (fwobj.gid, fwobj.nid))
        trgnode = self.nodeclient.get("%s_%s" % (fwobj.gid, targetNid))
        def get_backplane_ip(node):
            for mac, nicinfo in node.netaddr.iteritems():
                if nicinfo[0] == 'backplane1':
                    return nicinfo[1]
        srcip = get_backplane_ip(srcnode)
        trgip = get_backplane_ip(trgnode)
        sshkey = None
        sshpath = j.system.fs.joinPaths(j.dirs.cfgDir, 'sshkey')
        if j.system.fs.exists(sshpath):
            sshkey = j.system.fs.fileGetContents(sshpath)
        args = {'networkid': fwobj.id,
                'sourceip': srcip,
                'targetip': trgip,
                'sshkey': sshkey}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_migrate_routeros', nid=targetNid, gid=fwobj.gid, args=args)
        if job['state'] != 'OK':
            raise RuntimeError("Failed to move routeros check job %(guid)s" % job)
        fwobj.nid = targetNid
        self.osisvfw.set(fwobj)
        return True

    def fw_get_ipaddress(self, fwid, macaddress):
        fwobj = self.osisvfw.get(fwid)
        args = {'fwobject': fwobj.obj2dict(), 'macaddress': macaddress}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_get_ipaddress_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise RuntimeError("Failed to retreive IPAddress for macaddress %s. Error: %s" % (macaddress, job['result']['errormessage']))
        return job['result']

    def fw_set_password(self, fwid, username, password):
        fwobj = self.osisvfw.get(fwid)
        args = {'fwobject': fwobj.obj2dict(), 'username': username, 'password': password}
        job = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_set_password_routeros', gid=fwobj.gid, nid=fwobj.nid, args=args)
        if job['state'] != 'OK':
            raise RuntimeError("Failed to set password. Error: %s" % (job['result']['errormessage']))
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
                    raise RuntimeError("Failed to remove vfw with id %s" % fwid)
            self.osisvfw.delete(fwid)
        else:
            result = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_delete', nid=fwobj.nid, gid=fwobj.gid, args=args)['result']
            if result:
                self.osisvfw.delete(fwid)
            return result

    def _applyconfig(self, gid, nid, args):
        if args['fwobject']['type'] == 'routeros':
            result = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig_routeros', gid=gid, nid=nid, args=args)['result']
        else:
            result = self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig', gid=gid, nid=nid, args=args)['result']
        return result


    def fw_forward_create(self, fwid, gid, fwip, fwport, destip, destport, protocol='tcp', **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport str,,port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisvfw.get(fwid)
        rule = fwobj.new_tcpForwardRule()
        rule.fromAddr = fwip
        rule.fromPort = fwport
        rule.toAddr = destip
        rule.toPort = destport
        rule.protocol = protocol
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
        result = self._applyconfig(fwobj.gid, fwobj.nid, args)
        if result:
            self.osisvfw.set(fwobj)
        return result

    def fw_forward_delete(self, fwid, gid, fwip, fwport, destip, destport, protocol=None, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        param:fwip str,,adr on fw which will be visible to extenal world
        param:fwport port on fw which will be visble to external world
        param:destip adr where we forward to e.g. a ssh server in DMZ
        param:destport port where we forward to e.g. a ssh server in DMZ
        """
        fwobj = self.osisvfw.get(fwid)
        for rule in fwobj.tcpForwardRules:
            if rule.fromPort == fwport and rule.toAddr == destip and rule.toPort == destport and rule.fromAddr == fwip:
                if protocol and rule.protocol and rule.protocol != protocol:
                    continue
                fwobj.tcpForwardRules.remove(rule)
                args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': fwobj.obj2dict()}
                result = self._applyconfig(fwobj.gid, fwobj.nid, args)
                if result:
                    self.osisvfw.set(fwobj)
        return result


    def fw_forward_list(self, fwid, gid, **kwargs):
        """
        list all portformarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        result = list()
        for rule in fwobj.tcpForwardRules:
            result.append({'publicIp':rule.fromAddr, 'publicPort':rule.fromPort, 'localIp':rule.toAddr, 'localPort':rule.toPort, 'protocol': rule.protocol})
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

    def fw_start(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'action': 'start'}
        return self.agentcontroller.executeJumpscript('jumpscale', 'fw_action', gid=fwobj.gid, nid=fwobj.nid, args=args)['result']

    def fw_stop(self, fwid, gid, **kwargs):
        """
        param:fwid firewall id
        param:gid grid id
        """
        fwobj = self.osisvfw.get(fwid)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'action': 'stop'}
        self.agentcontroller.executeJumpscript('jumpscale', 'fw_action', gid=fwobj.gid, nid=fwobj.nid, args=args, wait=False)
        return True


    def ws_forward_create(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url
        """
        wsfobj = self.osisvfw.get(wsid)
        rule = wsfobj.new_wsForwardRule()
        rule.url = sourceurl
        rule.toUrls = desturls
        self.osisvfw.set(wsfobj)
        self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig', gid=wsfobj.gid, nid=wsfobj.nid, args={'name': wsfobj.name, 'fwobject': wsfobj.obj2dict()}, wait=False)
        return True


    def ws_forward_delete(self, wsid, gid, sourceurl, desturls, **kwargs):
        """
        param:wsid firewall id
        param:gid grid id
        param:sourceurl url which will match (e.g. http://www.incubaid.com:80/test/)
        param:desturls url which will be forwarded to
        """
        vfws = self.osisvfw.get(wsid)
        wsfr = vfws.wsForwardRules
        for rule in wsfr:
            if rule.url == sourceurl:
                desturls = desturls.split(',')
                urls = rule.toUrls.split(',')
                for dest in desturls:
                    if dest in rule.toUrls:
                        urls.remove(dest)
                rule.toUrls = ','.join(urls)
                if len(urls) == 0:
                    wsfr.remove(rule)
        args = {'name': '%s_%s' % (vfws.domain, vfws.name), 'action': 'start'}
        self.agentcontroller.executeJumpscript('jumpscale', 'vfs_applyconfig', gid=vfws.gid, nid=vfws.nid, args={'name': vfws.name, 'fwobject': vfws.obj2dict()}, wait=False)
        return True


    def ws_forward_list(self, wsid, gid, **kwargs):
        """
        list all loadbalancing rules (HTTP ONLY),
        ws stands for webserver
        is list of list [[$sourceurl,$desturl],..]
        can be 1 in which case its like simple forwarding, if more than 1 then is loadbalancing
        param:wsid firewall id (is also the loadbalancing webserver)
        param:gid grid id
        """
        result = list()
        vfws = self.osisvfw.get(wsid)
        wsfr = vfws.wsForwardRules
        for rule in wsfr:
            result.append([rule.url, rule.toUrls])
        return result
