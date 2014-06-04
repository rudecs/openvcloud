from JumpScale import j
from JumpScale.grid.osis.OSISStore import OSISStore


class mainclass(OSISStore):

    """
    Default object implementation
    """

    def init(self, path, namespace,categoryname):
        """
        gets executed when catgory in osis gets loaded by osiscmds.py (.init method)
        """
        self.initall( path, namespace,categoryname,db=True)
        masterdb=j.db.keyvaluestore.getRedisStore(namespace=self.dbprefix, host=j.application.config.get("rediskvs_master_addr"), port=7772, password=j.application.config.get("rediskvs_secret"), serializers=[self.json])
        self.db=j.db.keyvaluestore.getRedisStore(namespace=self.dbprefix, host='localhost', port=7771, password='', masterdb=masterdb, serializers=[self.json])
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



