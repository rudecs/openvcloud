from JumpScale import j
import os
import re
import tarfile
import subprocess
import base64


descr = """
gather statistics about OVS backends
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "upgrade"
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
    def execute_command(*args, **kwargs):
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        process = subprocess.Popen(*args, **kwargs)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(stderr)
        else:
            if stdout:
                print(stdout)
                return(stdout)

    if j.system.exists(repo_path):
        execute_command(['git','reset', '--hard' ], cwd=repo_path)
        execute_command(['git','checkout', 'master' ], cwd=repo_path)
        execute_command(['git','pull'], cwd=repo_path)
    else:
        execute_command(['git','clone', 'https://github.com/0-complexity/openvcloud_installer.git'],
                        cwd=zero_complexity_path)
    
    execute_command(['kubectl', 'apply', '-f', '%s/scripts/kubernetes/upgrader' % repo_path])
    
        

if __name__ == '__main__':
    print(action())
