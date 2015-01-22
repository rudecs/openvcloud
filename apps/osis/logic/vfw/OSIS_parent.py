from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStoreMongo):

    """
    Default object implementation
    """
