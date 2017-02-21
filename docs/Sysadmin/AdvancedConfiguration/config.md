# Advanced configurtation

In curtain situation its required to tweak some of our default values this can be changed on a per grid basis.
This section will explain how to set those configuration and which ones exists.


## Setting Advanced Configuration

Open `jsshell` on any node part of the grid you want to configure

```python
from cloudscalerlibcloud.utils.gridconfig import gridconfig
config = gridconfig()
config.set('<config key>', <config value>)
```

A config file can be any valid python object structure (simpletypes + list and dict) that is serializable as json.


## Getting Advanced Configuration

Open `jsshell` on any node part of the grid you want to configure

```python
from cloudscalerlibcloud.utils.gridconfig import gridconfig
config = gridconfig()
configvalue = config.get('<config key>')
```
