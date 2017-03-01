from . import cloudbroker
#from JumpScale.baselib.http_client.HttpClient import HTTPError
from JumpScale.portal.portal import exceptions
from JumpScale.portal.portal.PortalClient2 import ApiError

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
        try:
            return func(*args, **kwargs)
        except ApiError as e:
            ctype = e.response.headers['Content-Type'] or 'text/plain'
            headers = [('Content-Type', ctype), ]
            statuscode = e.response.status_code or 500
            raise exceptions.BaseError(statuscode, headers, e.response.content)

    return wrapper
