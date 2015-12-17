from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo

class mainclass(OSISStoreMongo):
    """
    Default object implementation
    """

    def set(self, key=None, value=None, waitIndex=False, session=None):
        _, counter = self._getMongoDB(session)
        key = "macaddress_%s" % key
        result = counter.find_and_modify({'_id': key}, {'$inc': {'seq': value}}, upsert=True)
        if result:
            return result['seq'] + value
        else:
            return value


