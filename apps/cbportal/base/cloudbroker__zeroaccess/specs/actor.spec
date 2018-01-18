[actor] @dbtype:mem,fs
    """
    0-access operations
    """
    method:listSessions
        """
        List available 0-access sessions
        """
        var:query string,, query to filter listing of sessions @optional
        var:remote string,, filter by remote machine address connected to in a session @optional
        var:user string,, filter by user used in a session @optional
        var:page int,, page number to list sessions from @optional
        result:list

    method:provision
        """
        Provision access to specified address
        """
        var:remote string,, ip of machine to connect to
        result:json

    method:downloadSession
        """
        Download session information for playback
        """
        var:session_id string,, session id
        result:json
    
    method:getSessionInitTime
        """
        List available 0-access sessions
        """
        result:json

    method:sessionTextSearch
        """
        Full text search on session activity
        """
        var:query string,, string to search for
        var:page int,, page number for search
        result:json

    

    