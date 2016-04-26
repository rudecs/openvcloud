from JumpScale import j

descr = """
Get openvpn config
"""

category = "vfw"
organization = "jumpscale"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(fwobject):
    from StringIO import StringIO
    host = fwobject['host']
    username = fwobject['username']
    password = fwobject['password']

    ro = j.clients.routeros.get(host, username, password)
    fp = StringIO()
    ro.download('ca.crt', fp)
    ca = fp.getvalue()
    config = """\
client
remote %s
port 1194
dev tap
proto tcp-client
nobind
cipher AES-128-CBC
script-security 2
up-restart
persist-key
persist-tun
ca ca.crt
auth-user-pass credentials
    """ % fwobject['pubips'][0]

    credentials = """\
vpn
%s
""" % j.tools.hash.sha1_string(ca)

    return {'ca.crt': ca,
            'credentials': credentials,
            'openvpn.ovpn': config}


