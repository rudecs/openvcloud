[actor] @dbtype:mem,fs
    """
    Operator actions for handling interventsions on a computenode
    """

    method:setStatus
        """
        Set the computenode status, options are 'ENABLED(creation and actions on machines is possible)','DISABLED(Only existing machines are started)', 'HALTED(Machine is not available'
        """
        var:name str,, name of the computenode
        var:status str,, status (ENABLED, DISABLED, HALTED).
        result: bool

    method:disable
        """
        Migrates all machines to different computes
        Set the status to 'DISABLED'
        """
        var:name str,, name of the computenode
        var:gridId int,, the grid this computenode belongs to
        result: bool
