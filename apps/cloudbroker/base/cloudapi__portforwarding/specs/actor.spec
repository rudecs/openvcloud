[actor] @dbtype:mem,fs
    """
    Portforwarding api
    uses actor /opt/code/jumpscale/unstable__jumpscale_grid/apps/vfw/actor/jumpscale__netmgr/
    """

    method:list
        """
        List all port forwarding rules in a cloudspace or machine
        """
        var:cloudspaceId int,,id of the cloudspace
        var:machineId int,,id of the machine, all rules of cloudspace will be listed if set to None @optional

    method:create
        """
        Create a port forwarding rule
        """
        var:cloudspaceId int,,id of the cloudspace
        var:publicIp str,, public ipaddress
        var:publicPort int,, public port
        var:machineId int,, id of the virtual machine
        var:localPort int,, local port
        var:protocol str,, protocol udp or tcp

    method:update
        """
        Update a port forwarding rule
        """
        var:cloudspaceId int,,id of the cloudspace
        var:id int,, id of the portforward to edit
        var:publicIp str,, public ipaddress
        var:publicPort int,, public port
        var:machineId int,, id of the virtual machine
        var:localPort int,, local port
        var:protocol str,, protocol udp or tcp

    method:delete
        """
        Delete a specific port forwarding rule
        """
        var:cloudspaceId int,, id of the cloudspace
        var:id int,, id of the port forward rule

    method:deleteByPort
        """
        Delete a specific port forwarding rule by public port details
        """
        var:cloudspaceId int,, id of the cloudspace
        var:publicIp str,, port forwarding public ip
        var:publicPort int,, port forwarding public port
        var:proto str,, port forwarding protocol @optional

    method:updateByPort
        """
        Shorthand method for delete and add
        update a specific port forwarding rule by public port details
        """
        var:cloudspaceId int,, id of the cloudspace
        var:sourcePublicIp str,, port forwarding public ip
        var:sourcePublicPort int,, port forwarding public port
        var:sourceProtocol str,, port forwarding protocol
        var:machineId int,, id of the virtual machine
        var:publicIp str,, port forwarding public ip
        var:publicPort int,, port forwarding public port
        var:localPort int,, local port
        var:protocol str,, port forwarding protocol @optional


