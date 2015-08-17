from JumpScale import j
import urllib

"""
this script execute the nexts actions on all the nodes specified in the nodes list:
    install JumpScale
    add the openvcloud domain to atyourservice.hrd
    configure the git login/passwd
    install bootstrap_node service
"""

gitlogin = ''
gitpasswd = ''
bootstrappURL = ''  # e.g: https://bootstrapdemo1.demo.greenitglobe.com/
nodes = [
    {
        'ip': '',
        'login': '',
        'passwd': '',
    }
]

ovcDomain = """metadata.openvcloud            =
    url:'https://git.aydo.com/0-complexity/openvcloud_ays',\n\n"""

for node in nodes:
    cl = j.ssh.connect(addr=node['ip'], port=22, passwd=node['passwd'], verbose=True, keypath=None)
    cl.fabric.api.env['user'] = node['login']
    cl.mode_sudo()
    # install jumpscale
    cl.run('curl https://raw.githubusercontent.com/Jumpscale/jumpscale_core7/master/install/install.sh > /tmp/js7.sh && bash /tmp/js7.sh')
    # add openvcloud domain to ays
    cl.file_append('/opt/jumpscale7/hrd/system/atyourservice.hrd', ovcDomain)
    # config git connection
    cl.run('jsconfig hrdset -n whoami.git.login -v "%s"' % gitlogin)
    cl.run('jsconfig hrdset -n whoami.git.passwd -v "%s"' % urllib.quote_plus(gitpasswd))
    # bootstrap node
    cl.run('ays install -n bootstrap_node --data instance.bootstrapp.addr=%s#' % bootstrappURL)
    # clean user/password in case it's sensitive information
    cl.run('jsconfig hrdset -n whoami.git.login -v ""')
    cl.run('jsconfig hrdset -n whoami.git.passwd -v ""')
