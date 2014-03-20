from JumpScale import j
import JumpScale.grid.agentcontroller
import JumpScale.lib.lxc
import JumpScale.baselib.serializers

class cloudapi_networkbuckets(j.code.classGetBase()):

    def __init__(self):
        self._te = {}
        self.actorname = "networkbuckets"
        self.appname = "cloudapi"
        self.client = j.core.osis.getClient(user='root')
        self.osisvfw = j.core.osis.getClientForCategory(self.client, 'vfw', 'virtualfirewall')
        self.agentcontroller = j.clients.agentcontroller.get()
        self.json = j.db.serializers.getSerializerType('j')

    def _getVfwObject(self, cloudspaceid):
        fwdict = self.osisvfw.simpleSearch({'domain': cloudspaceid})[0]
        return self.osisvfw.get(fwdict['fwid'])

    def fw_forward_create(self, cloudspaceid, gid, destip, destport, sourceip, sourceport, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        rule = fwobj.new_tcpForwardRule()
        rule.fromPort = destport
        rule.toAddr = sourceip
        rule.toPort = sourceport
        self.osisvfw.set(fwobj)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': self.json.dumps(fwobj)}
        return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=fwobj.nid, args=args)['result']

    def fw_forward_delete(self, cloudspaceid, gid, destip, destport, sourceip, sourceport, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        for rule in fwobj.tcpForwardRules:
            if rule.fromPort == destport and rule.toAddr == sourceip and rule.toPort == sourceport:
                fwobj.tcpForwardRules.remove(rule)
                args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': self.json.dumps(fwobj)}
                return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=fwobj.nid, args=args)['result']

        return False

    def fw_forward_list(self, cloudspaceid, gid, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        result = list()
        for rule in fwobj.tcpForwardRules:
            result.append([rule.fromPort, rule.toAddr, rule.toPort])

        return result

    def ws_forward_create(self, cloudspaceid, gid, sourceurl, desturls, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        rule = fwobj.new_wsForwardRule()
        rule.url = sourceurl
        rule.toUrls = desturls
        self.osisvfw.set(fwobj)
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': self.json.dumps(fwobj)}
        return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=fwobj.nid, args=args)['result']

    def ws_forward_delete(self, cloudspaceid, gid, sourceurl, desturls, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        wsfr = fwobj.wsForwardRules
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
        args = {'name': '%s_%s' % (fwobj.domain, fwobj.name), 'fwobject': self.json.dumps(fwobj)}
        return self.agentcontroller.executeJumpScript('jumpscale', 'vfs_applyconfig', nid=fwobj.nid, args=args)['result']

    def ws_forward_list(self, cloudspaceid, gid, **kwargs):
        fwobj = self._getVfwObject(cloudspaceid)
        result = list()
        for rule in fwobj.wsForwardRules:
            result.append([rule.url, rule.toUrls])
        return result