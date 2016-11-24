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
        var:networkid int,, Network ID
        var:publicgwip str,, Gateway of the public network
        var:publiccidr str,, CIDR of public network
        var:vlan int,,vlan tag
        #result:int #unique id of firewall

    method:fw_list @noauth
        """
        """
        var:gid int,,grid id
        var:domain str,,if not specified then all domains @tags: optional


    method:fw_delete @noauth
        """
        """
        var:fwid str,,firewall id
        var:gid int,,grid id


    method:fw_get_ipaddress @noauth
        """
        """
        var:fwid str,,firewall id
        var:macaddress str,,macaddress to retrieve ip for
        result:str #ipaddess


    method:fw_remove_lease @noauth
        """
        """
        var:fwid str,,firewall id
        var:macaddress str,,macaddress or list of macaddresses to release
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
        var:fwid str,,firewall id

    method:fw_move @noauth
        """
        will do some checks on firewall to see is running, is reachable over ssh, is connected to right interfaces
        """
        var:fwid str,,firewall full id
        var:targetNid int,,Target nid

    method:fw_stop @noauth
        """
        """
        var:fwid str,,firewall id

    method:fw_start @noauth
        """
        """
        var:fwid str,,firewall id

    method:fw_forward_list @noauth
        """
        list all portforwarding rules,
        is list of list [[$fwport,$destip,$destport]]
        1 port on source can be forwarded to more ports at back in which case the FW will do loadbalancing
        """
        var:fwid str,,firewall id
        var:gid int,,grid id
        var:localip str,,vmachine local ip address to filter with @tags: optional

    method:fw_forward_create @noauth
        """
        """
        var:fwid str,,firewall id
        var:gid int,,grid id
        var:fwip str,,addr on fw which will be visible to extenal world
        var:fwport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ

    method:fw_forward_delete @noauth
        """
        """
        var:fwid str,,firewall id
        var:gid int,,grid id
        var:fwip str,,adr where we forward to e.g. a ssh server in DMZ
        var:fwport int,,port on fw which will be visble to external world
        var:destip str,,adr where we forward to e.g. a ssh server in DMZ
        var:destport int,,port where we forward to e.g. a ssh server in DMZ
        var:protocol str,, protocol used to forward the port

    method:fw_get_openvpn_config
        """
        Get openvpn config
        """
        var:fwid str,,firewall id
