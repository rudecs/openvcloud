## Log Archive

Due to the limited root partition of the CPU and the storage nodes, the log rotation is configured rather small.

To prevent losing **valuable** log files, one can configure a log archive.

A log archive server can be any server reachable via ssh (`sftp`) from the CPU and storage nodes.

Configuration key: `log_server`
Configuration value: `{'host': 'some host', 'password': 'xxxxx', 'username': 'gig'}`

### Default values

No default values are provided for these settings.

When these settings are missing the log files will be truncated without any extra actions.
