from JumpScale import j

descr = """
Follow up creation of cloudspace routeros image
"""

name = "cloudbroker_accountcreate"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
queue = "hypervisor"
async = True


def _send_signup_mail(**kwargs):
    notifysupport = j.application.config.get("mothership1.cloudbroker.notifysupport")
    fromaddr = 'support@mothership1.com'
    toaddrs  =  [kwargs['email']]
    if notifysupport == '1':
        toaddrs.append('support@mothership1.com')


    html = """
<html>
<head></head>
<body>
    Dear %(user)s,<br>
    <br>
    Thank you for registering at Mothership<sup>1</sup>!<br>
    <br>
    We have now prepared your account %(username)s and we have applied a welcoming credit of $5 so you can start right away!<br>
    <br>
    Please confirm your e-mail address by following the activation link: <br>
    <br>
    <a href="%(portalurl)s/wiki_gcb/AccountActivation?activationtoken=%(activationtoken)s">%(portalurl)s/wiki_gcb/AccountActivation?activationtoken=%(activationtoken)s</a><br>
    <br>
    If you are unable to follow the link, please copy and paste it in your favourite browser.<br>
    <br>
    After your validation, you will be able to log in with your username and chosen password.<br>
    <br>
    Best Regards,<br>
    <br>
    The Mothership<sup>1</sup> Team<br>
    <a href="%(portalurl)s">www.mothership1.com</a><br>
</body>
</html>
""" % kwargs

    j.clients.email.send(toaddrs, fromaddr, "Mothership1 account activation", html, files=None)


def action(accountid, password, email, now, portalurl, token, username, user):
    import JumpScale.grid.osis
    import JumpScale.baselib.mailclient
    import JumpScale.portal

    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9999))
    secret = portalcfg.get('secret')
    cl = j.core.portal.getClient('127.0.0.1', port, secret)
    cloudspaceapi = cl.getActor('cloudapi','cloudspaces')

    cloudspaceapi.create(accountid, 'default', username, password=password)
    _send_signup_mail(username=username, user=user, email=email, portalurl=portalurl, activationtoken=token)

