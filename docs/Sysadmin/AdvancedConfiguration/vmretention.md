# Virtual machines retention period

This period will determine the period on which a deleted vm will remain in deleted state, which allows the user to restore the vm. After this period expires the machine will be destroyed and thus can't be restored.

- Configuration key: `delete_retention_period`
- Default value: `3600 * 24 * 7` (one week)

Note: Setting this value lower then 1 hour has no effect since the scheduler will run maxium one time an hour to check on the retention

