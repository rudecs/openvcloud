from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo

class mainclass(OSISStoreMongo):
    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False, session=None):
        key = "%(gid)s_%(id)s" % value
        value['guid'] = key
        db, counter = self._getMongoDB(session)
        if self.exists(key, session=session):
            orig = self.get(key, True, session=session)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            changed = False
            new = True
        db.save(value)
        return [key, new, changed]
