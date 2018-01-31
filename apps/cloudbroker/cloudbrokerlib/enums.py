from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

class BaseEnum(object):
    _ENUMS = list()

    @classmethod
    def _init(cls):
        for enum in cls._ENUMS:
            setattr(cls, enum, enum)

class MapEnum(BaseEnum):
    
    class Maaper(object):
        def __init__(self, provider):
            self.name = provider.name
        
        def __str__(self):
            return self.name

    @classmethod
    def _init(cls):
        for name, value in cls._ENUMS.iteritems():
            m = cls.Maaper(get_driver(name))
            for k, v in value.iteritems():
                setattr(m, k, v)
            setattr(cls, name, m)

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def getByValue(cls, num, provider_name):
        for name, value in cls._ENUMS[provider_name.lower()].iteritems():
            if value == num:
                return name

class MachineStatusMap(MapEnum):
    _ENUMS = {'libvirt':{'RUNNING': 1,
                         'HALTED': 5,
                         'PAUSED': 3},
              
              'openstack':{
                        'RUNNING': 0,
                        'HALTED': 2,
                        'PAUSED': 4,
                        'PENDING':3}
              }

MachineStatusMap._init()