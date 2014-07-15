class BaseEnum(object):
    _ENUMS = list()
    @classmethod
    def _init(cls):
        for enum in cls._ENUMS:
            setattr(cls, enum, enum)

class MachineStatus(BaseEnum):
    _ENUMS = ['RUNNING', 'HALTED', 'SUSPENDED']

MachineStatus._init()
