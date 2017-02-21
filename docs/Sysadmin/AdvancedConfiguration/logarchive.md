# Log Archive

Due to the limited root partition of the cpu nodes and the storagenodes our logrotation is configured rather small.
To prevent you from lossing `valuable` log files one can configure a log archive.

A log archive server is can be any server reachable via ssh (`sftp`) from the cpu and storage nodes

configuration key: `log_server`
configuration value: `{'host': 'somehost', 'password': 'xxxxx', 'username': 'gig'}`

## Default values

No default values are provided for these settings.
When these settings are missing the log files will be truncated withouth any extra actions.
