from JumpScale import j
from JumpScale.grid.osis.OSISStoreMongo import OSISStoreMongo


class mainclass(OSISStoreMongo):

    """
    Default object implementation
    """

    def set(self, key, value, waitIndex=False):
        id = value.get('id')
        if id and self.exists(id):
            orig = self.get(id)
            orig.update(value)
            value = orig
            changed = True
            new = False
        else:
            if not id:
                value['id'] = self.incrId()
            changed = False
            new = True
        value['guid'] = id
        self.client.save(value)
        return [id, new, changed]



