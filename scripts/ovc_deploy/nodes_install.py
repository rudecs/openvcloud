from JumpScale import j
from JumpScale.baselib import cmdutils
import urllib
import json

"""
this script execute the nexts actions on all the nodes specified in the nodes list:
    install JumpScale
    add the openvcloud domain to atyourservice.hrd
    configure the git login/passwd
    install bootstrap_node service
"""

ovcDomain = """metadata.openvcloud            =
    url:'https://git.aydo.com/0-complexity/openvcloud_ays',\n\n"""


def install(node, login, passwd, url):
    cl = j.ssh.connect(addr=node['ip'], port=22, passwd=node['passwd'], verbose=True, keypath=None)
    cl.fabric.api.env['user'] = node['login']
    cl.mode_sudo()
    # install jumpscale
    cl.run('apt-get update')
    cl.run('curl https://raw.githubusercontent.com/jumpscale7/jumpscale_core7/master/install/install.sh > /tmp/js7.sh')
    cl.run('bash /tmp/js7.sh')
    # add openvcloud domain to ays
    cl.file_append('/opt/jumpscale7/hrd/system/atyourservice.hrd', ovcDomain)
    # config git connection
    cl.run('jsconfig hrdset -n whoami.git.login -v "%s"' % login)
    cl.run('jsconfig hrdset -n whoami.git.passwd -v "%s"' % urllib.quote_plus(passwd))
    # bootstrap node
    cl.run('ays install -n bootstrap_node --data instance.bootstrapp.addr=%s#' % url)
    # clean user/password in case it's sensitive information
    cl.run('jsconfig hrdset -n whoami.git.login -v ""')
    cl.run('jsconfig hrdset -n whoami.git.passwd -v ""')


if __name__ == '__main__':
    parser = cmdutils.ArgumentParser()
    parser.add_argument("-l", "--login", help='gitlogin\n', required=True)
    parser.add_argument("-p", "--passwd", help='gitpasswd\n', required=True)
    parser.add_argument("-u", "--url", help='url to the bootstrapp\n', default='https://bootstrapscaleout1.demo.greenitglobe.com/', required=True)
    parser.add_argument("-n", "--nodes", help='path to a json file containing the nodes infos', default='nodes.json', required=True)
    args = parser.parse_args()

    content = j.system.fs.fileGetContents(args.nodes)
    nodes = json.loads(content)
    for node in nodes:
        install(node, args.login, args.passwd, args.url)
