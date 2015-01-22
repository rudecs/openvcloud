[actor] @dbtype:mem,fs
    """
    net manager
    """    
    method:fw_create @noauth
        """     
        """
        var:gid int,,grid id
        var:domain str,,needs to be unique name of a domain,e.g. a group, space, ... (just to find the FW back)
        var:login str,,Admin login to the firewall
        var:password str,, Admin password to the firewall
        var:publicip str,, Public IP of the firewall 
        var:type str,, Type of the firewall, e.g routeros, ...
        var:networkid str,, Network ID
        var:publicgwip str,, Gateway of the public network 
        var:publiccidr str,, CIDR of public network 
        #result:int #unique id of firewall

    method:fw_list @noauth
        """     
        """
        var:gid int,,grid id
        var:domain str,,if not specified then all domains @tags: optional


    method:fw_delete @noauth
        """     
        """
        var:fwid int,,firewall id
        var:gid int,,grid id


    method:fw_get_ipaddress @noauth
        """     
        """
        var:fwid str,,firewall id
        var:macaddress str,,macaddress to retrieve ip for
        result:str #ipaddess

    method:fw_set_password @noauth
        """     
        """
        var:fwid str,,firewall id
        var:username str,,username to set password for
        var:password str,,password to set

    method:fw_check @noauth
        """     
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        """
        var:fwid int,,firewall id
        var:gid int,,grid id

    method:fw_move @noauth
        """     
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        """
        var:fwid str,,firewall full id
        var:targetNid int,,Target nid

    method:fw_stop @noauth
        """     
        """
        var:fwid int,,firewall id
        var:gid int,,grid id

    method:fw_start @noauth
        """     
        """
        var:fwid int,,firewall id
        var:gid int,,grid id
        
    method:fw_forward_list @noauth
        """     
        list all portforwarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        """
        var:fwid int,,firewall id
        var:gid int,,grid id

    method:fw_forward_create @noauth
        """     
        """
        var:fwid int,,firewall id
        var:gid int,,grid id
        var:fwip str,,addr on fw which will be visible to extenal world
        var:fwport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ

    method:fw_forward_delete @noauth
        """     
        """
        var:fwid int,,firewall id
        var:gid int,,grid id
        var:fwip str,,adr where we forward to e.g. a ssh server in DMZ
        var:fwport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ

    method:ws_forward_list @noauth
        """
        list all loadbalancing rules (HTTP ONLY),
        ws stands for webserver
        is list of list [[$sourceurl,$desturl],..]
        can be 1 in which case its like simple forwarding, if more than 1 then is loadbalancing
        """
        var:wsid int,,firewall id (is also the loadbalancing webserver)
        var:gid int,,grid id

    method:ws_forward_create @noauth
        """     
        """
        var:wsid int,,firewall id
        var:gid int,,grid id
        var:sourceurl str,,url which will match (e.g. http://www.incubaid.com:80/test/)
        var:desturls str,,url which will be forwarded to (e.g. http://192.168.10.1/test/) can be more than 1 then loadbalancing; if only 1 then like a portforward but matching on url

    method:ws_forward_delete @noauth
        """     
        """
        var:wsid int,,firewall id
        var:gid int,,grid id
        var:sourceurl str,,url which will match (e.g. http://www.incubaid.com:80/test/)
        var:desturls str,,url which will be forwarded to

