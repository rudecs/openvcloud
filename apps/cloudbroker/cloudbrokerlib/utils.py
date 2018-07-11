from JumpScale import j

def removeConfusingChars(input):
    return input.replace('0', '').replace('O', '').replace('l', '').replace('I', '')


class Dummy(object):

    def __init__(self, **kwargs):
        self.extra = {}
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

def getJobTags():
    requestid = j.core.portal.active.requestContext.env.get('JS_AUDITKEY')
    tags = []
    if requestid:
        tags.append('requestid:{}'.format(requestid))
    return tags

