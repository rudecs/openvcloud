from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore
ujson = j.db.serializers.getSerializerType('j')


class mainclass(OSISStore):

    """
    Default object implementation
    """

    def init(self, path, namespace,categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall( path, namespace,categoryname,db=True)
        self.db=j.db.keyvaluestore.getRedisStore(namespace='', host='localhost', port=7771, password='', masterdb=masterdb)
        self.db.osis[self.dbprefix]=self


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



