from JumpScale import j
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor
import requests
from urlparse import urlparse
from os import path as os_path
import yaml

class cloudbroker_grid(BaseActor):

    def __init__(self):
        super(cloudbroker_grid, self).__init__()
        self.sysmodels = j.clients.osis.getNamespace('system')
        self.acl = j.clients.agentcontroller.get()
        self.pcl = j.clients.portal.getByInstance('main')

    @auth(['level1', 'level2', 'level3'])
    def purgeLogs(self, gid, age='-3d', **kwargs):
        return self.acl.executeJumpscript('cloudscalers', 'logs_purge', args={'age': age}, gid=gid, role='master', wait=False)['result']

    @auth(['level1', 'level2', 'level3'])
    def checkVMs(self, **kwargs):
        sessions = self.acl.listSessions()
        for nodeid, roles in sessions.iteritems():
            if 'master' in roles:
                gid = int(nodeid.split('_')[0])
                self.acl.executeJumpscript('jumpscale', 'vms_check', gid=gid, role='master', wait=False)
        return 'Scheduled check on VMS'


    @auth(['level1', 'level2', 'level3'])
    def rename(self, name, gid, **kwargs):
        location = next(iter(self.models.location.search({'gid': gid})[1:]), None)
        if not location:
            raise exceptions.NotFound('Could not find location with gid %s' % gid)
        location['name'] = name
        self.models.location.set(location)
        return True

    @auth(['level1', 'level2', 'level3'])
    def add(self, name, gid, locationcode, **kwargs):
        location = next(iter(self.models.location.search({'gid': gid})[1:]), None)
        if location:
            raise exceptions.Conflict("Location with gid %s already exists" % gid)
        location = self.models.location.new()
        location.gid = gid
        location.flag = 'black'
        location.locationCode = locationcode
        location.name = name
        self.models.location.set(location)
        return 'Location has been added successfully, do not forget to add networkids and public IPs'

    @auth(['level1', 'level2', 'level3'])
    def upgrade(self, url, **kwargs):
        manifest = requests.get(url).content
        version = os_path.splitext(os_path.basename(urlparse(url).path))[0]
        current_time = j.base.time.getTimeEpoch()
        if self.sysmodels.version.count({'name': version}) > 0:
            self.sysmodels.version.updateSearch({'name': version}, {'$set': {'creationTime': current_time, 'status': 'INSTALLING'}})
        else:
            versionmodel = self.sysmodels.version.new()
            versionmodel.name = version
            versionmodel.url = url
            versionmodel.manifest = manifest
            versionmodel.creationTime = current_time
            versionmodel.status = 'INSTALLING'
            self.sysmodels.version.set(versionmodel)

        gids = [ x['gid'] for x in self.models.location.search({'$fields': ['gid']})[1:]]
        for gid in gids:
            self.acl.executeJumpscript('greenitglobe', 'delete_file', role='controllernode', gid=gid, wait=True, all=True, args={'path': '/var/ovc/updatelogs/update_env.log'})
            self.acl.executeJumpscript('greenitglobe', 'upgrade_cluster', role='controllernode',gid=gid, wait=False)
        return {'redirect_url': '/updating'}

    @auth(['level1', 'level2', 'level3'])
    def runUpgradeScript(self, **kwargs):
        current_version = self.sysmodels.version.searchOne({'status': 'CURRENT'})['name']
        previous_version_dict = self.sysmodels.version.searchOne({'status': 'PREVIOUS'})
        if previous_version_dict:
            previous_version = previous_version_dict['name']
        else:
            previous_version = current_version
        location_url = self.pcl.actors.cloudapi.locations.getUrl()
        job = self.acl.executeJumpscript('greenitglobe', 'upgrader', role='master', gid=j.application.whoAmI.gid,
                                        wait=True, args={'previous_version': previous_version,
                                                         'current_version': current_version,
                                                         'location_url': location_url})
        if job['state'] != 'OK':
            raise exceptions.Error("Couldn't execute upgrade script")
        return 'Upgrade script ran successfully'

    @auth(['level1', 'level2', 'level3'])
    def changeSettings(self, id, settings, **kwargs):
        if self.sysmodels.grid.count({'id': id}) == 0:
            raise exceptions.NotFound("No grid with id {} was found".format(id))
        try:
            settings = yaml.load(settings)
        except:
            raise exceptions.BadRequest("settings needs to be in valid YAML format")
        if not isinstance(settings, dict):
            raise exceptions.BadRequest("settings needs to be in valid YAML format and needs to be an object")
        self.sysmodels.grid.updateSearch({'id': id}, {'$set': {'settings': settings}})
        return 'Changing settings done successfully'

        
    @auth(['level2', 'level3'], True)
    def executeMaintenanceScript(self, gid, nodestype, script, **kwargs):
        ctx = kwargs['ctx']
        ctx.events.runAsync(self._executeMaintenanceScript,
                            args=(int(gid), nodestype, script),
                            kwargs=kwargs,
                            title='Executing maintenance script',
                            success='Maintenance Script executed successfully',
                            error='Failed to execute maintenance script')

    @auth(['level1', 'level2', 'level3'])
    def _executeMaintenanceScript(self, gid, nodestype, script, **kwargs):
        if nodestype == 'both':
            nodestype = ['cpunode', 'storagenode']
        else:
            nodestype = [nodestype]

        sessions = self.acl.listSessions()
        for nodeid, roles in sessions.iteritems():
            node_actor = j.apps.cloudbroker.node
            nid = int(nodeid.split('_')[1])
            if int(nodeid.split('_')[0]) == gid:
                if set(roles) & set(nodestype): # check of there is intersection between nodestype and roles
                    # put node in maintenance
                    node_actor.maintenance(nid, gid, 'stop', **kwargs)
                    # execute the script via agentcontroller
                    node_actor.execute_script(nid, gid, script)
                    # enable it again
                    node_actor.enable(nid, gid, 'Back from maintenance', **kwargs)
        return "Script Executed"
        
        
