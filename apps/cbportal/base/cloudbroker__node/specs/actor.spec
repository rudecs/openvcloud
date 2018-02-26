[actor] @dbtype:mem,fs
    """
    Operator actions on nodes
    """
    method:unscheduleJumpscripts
        """
        unschedules periodic jumpscripts.
        """
        var:nid int,, id of the node
        var:gid int,, the grid this node belongs to
        var:category str,, name of the category of jumpscripts to unschedule @optional
        var:name str,,name of the jumpscript to unschedule @optional

    method:scheduleJumpscripts
        """
        schedules  jumpscripts for periodic execution
        """
        var:nid int,, id of the node
        var:gid int,, the grid this node belongs to
        var:category str,, name of the category of jumpscripts to schedule @optional
        var:name str,,name of the jumpscript to schedule @optional