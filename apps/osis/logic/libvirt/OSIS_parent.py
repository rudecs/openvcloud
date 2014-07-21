from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo


class mainclass(OSISStoreMongo):
    MULTIGRID = False

    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False):
        id = value.get('id')
        if id and self.exists(id):
            orig = self.get(id, True)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                id = self.incrId()
                value['id'] = id
            changed = False
            new = True
        value['guid'] = id
        self.client.save(value)
        return [id, new, changed]
