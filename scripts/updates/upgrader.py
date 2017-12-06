from JumpScale import j
import os
import sys
import json
UPGRADEFOLDER = '/opt/code/github/0-complexity/openvcloud/libs/agent-scripts/cloudbroker/upgrades/'

def main(options):
    versionfolder = os.path.join(UPGRADEFOLDER, options.version)
    if not os.path.exists(versionfolder):
        j.console.info('Versionfolder does not exist nothing to do')
        sys.exit(0)

    acl = j.clients.agentcontroller.get()
    ccl = j.clients.osis.getNamespace('cloudbroker')
    pcl = j.clients.portal.getByInstance('main')
    locationurl = pcl.actors.cloudapi.locations.getUrl()

    locationgids = [loc['gid'] for loc in ccl.location.search({})[1:]]
    for role in j.system.fs.listDirsInDir(versionfolder, dirNameOnly=True):
        if role == 'master':
            gids = [j.application.whoAmI.gid]
        else:
            gids = locationgids
        rolefolder = os.path.join(versionfolder, role)
        for script in j.system.fs.listFilesInDir(rolefolder):
            name = j.system.fs.getBaseName(script)
            name, ext = os.path.splitext(name)
            if ext != '.py':
                continue
            j.console.info('Executing {} on {}'.format(name, role))
            for gid in gids:
                jobs = acl.executeJumpscript(name=name, organization='greenitglobe', role=role, gid=gid, all=True)
                errors = False
                for job in jobs:
                    if job['state'] == 'ERROR':
                        errors = True
                        try:
                            eco = json.loads(job['result'])['guid']
                        except:
                            eco = False
                        if eco:
                            j.console.warning('Failed to execute {} on {} see "{}/grid/error%20condition?id={}'.format(name, job['nid'], locationurl, eco))
                        else:
                            j.console.warning('Failed to execute {} on {} see: {}'.format(name, job['nid'], job['result']))
                    if job['state'] == 'TIMEOUT':
                        errors = True
                        j.console.warning('Failed to execute {} on {} in reasonable time is not up?'.format(name, job['nid']))
                if errors:
                    sys.exit(1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', help='Version of upgrade scripts to run')
    options = parser.parse_args()
    main(options)
