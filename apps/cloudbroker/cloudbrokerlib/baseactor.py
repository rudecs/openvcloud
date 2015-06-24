from . import cloudbroker
from JumpScale.baselib.http_client.HttpClient import HTTPError

from JumpScale import j

class BaseActor(object):
    def __init__(self):
        self.cb = cloudbroker.CloudBroker()
        self.models = cloudbroker.models
        if self.__class__.__name__.startswith('cloudapi'):
            packagename = 'cloudbroker'
        elif self.__class__.__name__.startswith('cloudbroker'):
            packagename = 'cbportal'
        self.hrd = j.atyourservice.get(name=packagename, instance='main').hrd

def wrap_remote(func):
    def wrapper(*args, **kwargs):
        ctx = kwargs['ctx']
        try:
            return func(*args, **kwargs)
        except HTTPError, e:
            ctype = e.httperror.headers.type or 'text/plain'
            headers = [('Content-Type', ctype), ]
            statuscode = e.status_code or 500
            ctx.start_response("%s" % statuscode, headers)
            return e.msg

    return wrapper
