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
    zero_complexity_path = '/opt/code/github/0-complexity/'
    repo_path = zero_complexity_path + 'openvcloud_installer'

    if j.system.fs.exists(repo_path):
        j.system.process.execute('cd %s && git reset --hard' % repo_path)
        j.system.process.execute('cd %s && git checkout master' % repo_path)
        j.system.process.execute('cd %s && git pull' % repo_path)
    else:
        j.system.process.execute(
            'cd %s && git clone https://github.com/0-complexity/openvcloud_installer.git' % zero_complexity_path)

    j.system.process.execute('kubectl --kubeconfig /etc/kubernetes/admin.conf apply -f %s/scripts/kubernetes/upgrader' % repo_path, outputToStdout=True)


if __name__ == '__main__':
    print(action())
