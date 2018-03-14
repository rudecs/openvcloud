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
    
    method:maintenance
        """
        Place node in maintenance state
        """
        var:nid int,,nids of storagerouter
        var:gid int,, the grid this node belongs to
        var:vmaction str,, what to do with running vms move or stop @optional

    method:enable
        """
        Enable node from maintenance status to enabled 
        """
        var:nid int,,nids of storagerouter
        var:gid int,, the grid this node belongs to
        var:message str,,message. Must be less than 30 characters @optional

    method:decomission
        """
        Set node status to 'DECOMMISSIONED' and remove from relevant process for vms and markoff for storage routers
        """
        var:nid int,,nid of storagerouter
        var:gid int,, the grid this node belongs to
        var:vmaction str,, what to do with running vms move or stop @optional