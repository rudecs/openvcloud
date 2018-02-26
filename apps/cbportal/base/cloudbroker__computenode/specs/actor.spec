[actor] @dbtype:mem,fs
    """
    Operator actions for handling interventsions on a computenode
    """

    method:setStatus
        """
        Set the computenode status, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available'
        """
        var:id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:status str,, status (ENABLED, MAINTENANCE, DECOMMISSIONED).
        result: str

    method:btrfs_rebalance
        """
        Rebalances the btrfs filesystem
        """
        var:name str,, name of the computenode
        var:gid int,, the grid this computenode belongs to
        var:mountpoint str,,the mountpoint of the btrfs
        var:uuid str,,if no mountpoint given, uuid is mandatory
        result: bool

    method:enable
        """
        Enable a stack
        """
        var:id int,,id of the computenode
        var:gid int,,the grid this computenode belongs to
        var:message str,,message. Must be less than 30 characters
        result: str

    method:enableStacks
        """
        Enable stacks
        """
        var:ids list(int),,ids of stacks to enable
        result:bool

    method:list
        """
        List stacks
        """
        var:gid int,,filter on gid @optional
        result:list

    method:maintenance
        """
        Migrates or stop all vms
        Set the status to 'MAINTENANCE'
        """
        var:id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:vmaction str,, what to do with running vms move or stop
        var:message str,,message. Must be less than 30 characters
        result: str

    method:unscheduleJumpscripts
        """
        unschedules periodic jumpscripts.
        """
        var:stack_id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:category str,, name of the category of jumpscripts to unschedule @optional
        var:name str,,name of the jumpscript to unschedule @optional

    method:scheduleJumpscripts
        """
        schedules  jumpscripts for periodic execution
        """
        var:stack_id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:category str,, name of the category of jumpscripts to schedule @optional
        var:name str,,name of the jumpscript to schedule @optional

    method:decommission
        """
        Migrates all machines to different computes
        Set the status to 'DECOMMISSIONED'
        """
        var:id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:message str,,message. Must be less than 30 characters
        result: str
