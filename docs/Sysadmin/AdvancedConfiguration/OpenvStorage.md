## Open vStorage Settings


### Configuring edge client username/password

Configuration key: `ovs_credentials`  
Configuration value: `{'edgeuser': 'edgke', 'edgepassword': 'plaintextpwd'}`

> Note:
Be carefull when setting these credentials since ovs_credentials already contains the master IPs we need to make sure we do not overwrite them
```
from CloudscalerLibcloud.utils.gridconfig import GridConfig
cfg = GridConfig()
ovscred = cfg.get('ovs_credentials', {})
ovscred['edgeuser'] = 'edgke'
ovscred['edgepassword'] = 'plaintextpwd'
cfg.set('ovs_credentials', ovscred)
```

### Setting metadata cache percentage.

Configuration key: `ovs_settings`  
Configuration value: `{'vpool_vmstor_metadatacache': 20, 'vpool_data_metadatacache': 20}`
