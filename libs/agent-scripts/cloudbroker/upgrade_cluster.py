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
    manifest['version'] = versionmodel['name']
    manifest['url'] = versionmodel['url']
    for repo in manifest['repos']:
        if repo['url'] == 'https://github.com/0-complexity/openvcloud_installer':
            tag = repo['target'].get('tag')
            branch = repo['target'].get('branch')
            break

    try:
        with open('/tmp/versions-manifest.yaml', 'w+') as file_descriptor:
            yaml.dump(manifest, file_descriptor)        
            j.system.process.execute('kubectl --kubeconfig /root/.kube/config create configmap --dry-run -o yaml --from-file=/tmp/versions-manifest.yaml versions-manifest |  kubectl --kubeconfig /root/.kube/config apply -f -')
    finally:
        j.system.fs.remove('/tmp/versions-manifest.yaml')
    
    j.do.pullGitRepo('https://github.com/0-complexity/openvcloud_installer/', ignorelocalchanges=True, reset=True,
                     tag=tag, branch=branch)
    j.system.process.execute('kubectl apply --kubeconfig /root/.kube/config -f %s/scripts/kubernetes/upgrader/upgrader-job.yaml' % repo_path, outputToStdout=True)


if __name__ == '__main__':
    print(action())
