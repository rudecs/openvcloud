[actor] @dbtype:mem,fs
    """
    vfw manager
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/
    uses osis model /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/osis/vfw/
    """    
        
    method:fw_forward_list @noauth
        """     
        list all portforwarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id

    method:fw_forward_create @noauth
        """     
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id
        var:sourceip str,,adr where we forward to e.g. a ssh server in DMZ
        var:sourceport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ

    method:fw_forward_delete @noauth
        """     
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id
        var:sourceip str,,adr where we forward to e.g. a ssh server in DMZ
        var:sourceport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ

    method:ws_forward_list @noauth
        """
        list all loadbalancing rules (HTTP ONLY),
        ws stands for webserver
        is list of list [[$sourceurl,$desturl],..]
        can be 1 in which case its like simple forwarding, if more than 1 then is loadbalancing
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id

    method:ws_forward_create @noauth
        """     
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id
        var:sourceurl str,,url which will match (e.g. http://www.incubaid.com:80/test/)
        var:desturls str,,url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url

    method:ws_forward_delete @noauth
        """     
        """
        var:cloudspaceid int,,id of space
        var:gid int,,grid id
        var:sourceurl str,,url which will match (e.g. http://www.incubaid.com:80/test/)
        var:desturls str,,url which will be forwarded to

