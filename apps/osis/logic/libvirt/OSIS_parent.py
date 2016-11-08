from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo

class mainclass(OSISStoreMongo):
    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False, session=None):
        id = value.get('id')
        db, counter = self._getMongoDB(session)
        if id and self.exists(id, session=session):
            orig = self.get(id, True, session=session)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.incrId(counter)
                value['id'] = id
            changed = False
            new = True
        if isinstance(id, basestring):
#            id = id.replace('-', '')
            value['id'] = id
        value['guid'] = id
        db.save(value)
        return [id, new, changed]
