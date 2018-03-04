[actor] @dbtype:mem,fs
    """
    Operator actions for handling interventions on a a grid
    """

    method:purgeLogs
        """
        Remove logs & eco’s
        By default the logs en eco's older than than 1 week but this can be overriden
        """
        var:gid int,, id of the grid
        var:age str,, by default 1 week (-1h, -1w TODO: check the options in the jsgrid purgelogs)
        result: bool

    method:checkVMs
        """
        Run checkvms jumpscript
        """
        var:gid int,, id of the grid
        result: bool

    method:rename
        """
        Rename a grid/location
        """
        var:gid int,, id of the grid
        var:name str,, New name of the location @validator:name
        result: bool

    method:add
        """
        Adds a location/grid
        """
        var:gid int,, id of the grid
        var:name str,, Name of the location @validator:name
        var:locationcode str,, Location code typicly used in dns names
        result: str

    method:upgrade
        """
        upgrade the grid to the latest
        """
        var:url str,, Version to update to
    
    method:runUpgradeScript
        """
        Run version migration scripts
        """
        result: str
        