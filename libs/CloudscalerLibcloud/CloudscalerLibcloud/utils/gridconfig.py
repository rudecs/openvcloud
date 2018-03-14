from JumpScale import j
from psutil import virtual_memory

# for thin provisioning
TOTAL_MEM = int(virtual_memory().total >> 30)
DELETE_RETENTION_PERIOD = 3600 * 24 * 7 # one week

def get_reserved_memory_default(total_mem):
    if total_mem <= 64:
        return 1024  # 1 GB
    elif 64 < TOTAL_MEM < 196:
        return 2048  # 2 GB
    else:
        return 4096  # 4 GB

RESERVED_MEM = get_reserved_memory_default(TOTAL_MEM)

class GridConfig(object):
    def __init__(self, grid=None, total_mem=int(virtual_memory().total >> 30)):
        self._scl = None
        self.default = {
            "reserved_mem": get_reserved_memory_default(total_mem),
            "delete_retention_period": DELETE_RETENTION_PERIOD
        }
        if grid is None:
            self.gid = j.application.whoAmI.gid
            self.grid = self.scl.grid.get(self.gid)
        else:
            self.gid = grid.id
            self.grid = grid            
        self.settings = self.grid.settings

    @property
    def scl(self):
        if self._scl is None:
            self._scl = j.clients.osis.getNamespace('system')
        return self._scl

    def refresh_settings(self):
        self.grid = self.scl.grid.get(self.gid)
        self.settings = self.grid.settings

    def set(self, key, value):
        self.settings[key] = value
        return self.scl.grid.updateSearch({"guid": self.gid}, {"$set": {"settings.%s" % key: value}})

    def get(self, key, default=None):
        return self.settings.get(key, self.default.get(key, default))
