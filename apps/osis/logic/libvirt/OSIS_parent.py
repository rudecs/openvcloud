from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False):
        id = value.get('id')
        if id and self.db.exists(self.dbprefix, id):
            orig = self.get(id)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.db.increment(self.dbprefix_incr)
                value['id'] = id
            changed = False
            new = True
        value['guid'] = id
        self.db.set(self.dbprefix, key=id, value=value)
        self.index(value)
        return [id, new, changed]





