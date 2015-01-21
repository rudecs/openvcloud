[actor] @dbtype:mem,fs
    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/
    """

    method:list
        """
        list all portforwarding rules.
        """
        var:cloudspaceid int,,id of the cloudspace

    method:create
        """
        Create a portforwarding rule
        """
        var:cloudspaceid int,,id of the cloudspace
        var:publicIp str,, public ipaddress
        var:publicPort int,, public port
        var:vmid int,, id of the vm
        var:localPort int,, local port
        var:protocol str,, protocol udp or tcp

    method:update
        """
        Update a porforwarding rule
        """
        var:cloudspaceid int,,id of the cloudspace
        var:id int,, id of the portforward to edit
        var:publicIp str,, public ipaddress
        var:publicPort int,, public port
        var:vmid int,, id of the vm
        var:localPort int,, local port
        var:protocol str,, protocol udp or tcp

    method:delete
        """
        Delete a specific portforwarding rule
        """
        var:cloudspaceid int,, if of the cloudspace
        var:id int,, id of the portforward
