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
        var:status str,, status (ENABLED, DISABLED, HALTED).
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

    method:disable
        """
        Migrates all machines to different computes
        Set the status to 'DISABLED'
        """
        var:id int,, id of the computenode
        var:gid int,, the grid this computenode belongs to
        var:message str,,message. Must be less than 30 characters
        result: str
