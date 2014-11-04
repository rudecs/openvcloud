class BaseEnum(object):
    _ENUMS = list()

    @classmethod
    def _init(cls):
        for enum in cls._ENUMS:
            setattr(cls, enum, enum)

class MapEnum(BaseEnum):

    @classmethod
    def _init(cls):
        for name, value in cls._ENUMS.iteritems():
            setattr(cls, name, value)

    @classmethod
    def getByValue(cls, num):
        for name, value in cls._ENUMS.iteritems():
            if value == num:
                return name

class MachineStatus(BaseEnum):
    _ENUMS = ['RUNNING', 'HALTED', 'SUSPENDED']

class MachineStatusMap(MapEnum):
    _ENUMS = {'RUNNING': 1, 'HALTED': 4, 'SUSPENDED': 3}


MachineStatus._init()