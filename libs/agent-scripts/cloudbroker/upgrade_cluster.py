from JumpScale import j

descr = """
Runs the upgrade pod from the openvcloud_installer repo that upgrades the location.
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "cloudbroker"
roles = ['controllernode']
timeout = 120
order = 1
async = True


def action():
    """
    initiate upgrade
    """
    import yaml
    zero_complexity_path = '/opt/code/github/0-complexity/'
    repo_path = zero_complexity_path + 'openvcloud_installer'
    scl = j.clients.osis.getNamespace('system')
    versionmodel = scl.version.searchOne({'status': 'INSTALLING'})
    manifest = yaml.load(versionmodel['manifest'])
    for repo in manifest['repos']:
        if repo['url'] == 'https://github.com/0-complexity/openvcloud_installer':
            tag = repo['target']['tag']
            break

    j.system.process.execute('kubectl delete configmap manifest-version', dieOnNonZeroExitCode=False)
    j.system.process.execute('kubectl create configmap manifest-version --from-literal=software.version={version}'.format(version=versionmodel['name']))
    j.do.pullGitRepo('https://github.com/0-complexity/openvcloud_installer/', ignorelocalchanges=True, reset=True, tag=tag)
    j.system.process.execute('kubectl apply -f %s/scripts/kubernetes/upgrader/upgrader-job.yaml' % repo_path, outputToStdout=True)



if __name__ == '__main__':
    print(action())
