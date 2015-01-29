from . import cloudbroker
from JumpScale import j

class BaseActor(object):
    def __init__(self):
        self.cb = cloudbroker.CloudBroker()
        self.models = cloudbroker.models
        if self.__class__.__name__.startswith('cloudapi'):
            packagename = 'cloudbroker'
        elif self.__class__.__name__.startswith('cloudbroker'):
            packagename = 'cbportal'
        self.hrd = j.packages.get(name=packagename, instance='main').hrd

