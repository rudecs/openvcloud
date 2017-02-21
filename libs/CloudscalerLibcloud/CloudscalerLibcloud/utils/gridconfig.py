from JumpScale import j
from psutil import virtual_memory

# for thin provisioning
TOTAL_MEM = int(virtual_memory().total >> 30)
if TOTAL_MEM <= 64:
    RESERVED_MEM = 1024  # 1 GB
elif 64 < TOTAL_MEM < 196:
    RESERVED_MEM = 2048  # 2 GB
else:
    RESERVED_MEM = 4096  # 4 GB

class GridConfig:

    def __init__(self):
        self.scl = j.clients.osis.getNamespace('system')
        self.default = {
            "reserved_mem": RESERVED_MEM,
        }
        self.gid = j.application.whoAmI.gid
        self.grid = self.scl.grid.get(self.gid)
        self.settings = self.grid.settings

    def refresh_settings(self):
        self.grid = self.scl.grid.get(self.gid)
        self.settings = self.grid.settings

    def set(self, key, value):
        self.settings[key] = value
        return self.scl.grid.updateSearch({"guid": self.gid}, {"$set": {"settings.%s" % key: value}})

    def get(self, key):
        return self.settings.get(key, self.default.get(key, None))
