## Advanced Configuration

In certain situations it is required to tweak some of our default values. This can be changed on a per grid basis.

This section will explain how to set those configuration and which ones exist.

Here below we discuss how to:

- [Setting advanced configuration values](#set)
- [Getting advanced configuration values](#get)

This can be applied to the following configuration settings:

- [Log Archive](LogArchive.md)
- [Open vStorage settings](OpenvStorage.md)
- [Reservation of Host Memory](ReservedHostMemory.md)
- [Virtual machines retention period](vmretention.md)


<a id="set"></a>
### Setting values

Open `jsshell` on any node that is part of the grid you want to configure, and type:

```python
from CloudscalerLibcloud.utils.gridconfig import GridConfig
config = GridConfig()
config.set('<config key>', <config value>)
```

A config file can be any valid Python object structure (simple types + list and dict) that is serializable as JSON.


<a id="get"></a>
### Getting values

Open `jsshell` on any node that is part of the grid you want to configure, and type:

```python
from CloudscalerLibcloud.utils.gridconfig import GridConfig
config = gridconfig()
configvalue = config.get('<config key>')
```
