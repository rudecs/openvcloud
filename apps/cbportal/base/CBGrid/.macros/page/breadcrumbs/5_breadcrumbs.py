import re

def main(j, args, inparams, tags, tasklet):
    page = args.page
    doc = args.doc
    pagename = doc.original_name.lower()
    breadcrumbs = [('/CBGrid/', 'Cloud Broker Portal'), ]
    params = args.requestContext.params.copy()


    if pagename == 'user':
        breadcrumbs.append(('users', 'Users'))
        id = params['id']
        breadcrumbs.append(('user?id=%(id)s' % params, id.split('_', 1)[-1]))
    elif pagename == 'account':
        breadcrumbs.append(('accounts', 'Accounts'))
        id = params['id']
        breadcrumbs.append(('account?id=%(id)s' % params, id))
    elif pagename == 'cloudspace':
        breadcrumbs.append(('cloudspaces', 'CloudSpaces'))
        id = params['id']
        breadcrumbs.append(('cloudspace?id=%(id)s' % params, id))
    elif pagename == 'vmachine':
        breadcrumbs.append(('vmachines', 'vMachines'))
        id = params['id']
        breadcrumbs.append(('vmachine?id=%(id)s' % params, id))
    elif pagename == 'image':
        breadcrumbs.append(('images', 'Images'))
        id = params['id']
        breadcrumbs.append(('image?id=%(id)s' % params, id))
    elif pagename == 'network':
        breadcrumbs.append(('networks', 'Networks'))
        id = params['id']
        breadcrumbs.append(('network?id=%(id)s' % params, id))
    elif pagename == 'stack':
        breadcrumbs.append(('stacks', 'Stacks'))
        id = params['id']
        breadcrumbs.append(('stack?id=%(id)s' % params, id))
    else:
        breadcrumbs.append((pagename, pagename.capitalize()))

    data = "<ul class='breadcrumb'>%s</ul>"
    innerdata = ""
    for link, title in breadcrumbs[:-1]:
        innerdata += "<li><a href='%s'>%s</a><span style='opacity: 0.5; margin-right: 8px; margin-left: 2px;' class='icon-chevron-right'></span></li>" % (link, title)
    innerdata += "<li class='active'>%s</li>" % breadcrumbs[-1][1]

    page.addMessage(data % innerdata)
    inparams.result = page
    return inparams


def match(j, args, params, tags, tasklet):
    return True
