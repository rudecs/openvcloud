from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    actors = j.apps.cloudbroker.iaas.cb.extensions.imp.actors.cloudapi
    params.result = page = args.page
    cloudspaceId = args.getTag('cloudspaceId')
    defenseinfo = actors.cloudspaces.getDefenseShield(cloudspaceId)
    defenseinfo['name'] = "autologin=%(user)s|%()s"

    page.addHTML("""<a href="javascript:window.open('%(url)s', 'autologin=%(user)s%%7c%(password)s');javascript:void(0);">Defenseshield</a>""" % defenseinfo)

    return params

def match(j, args, params, tags, tasklet):
    return True
