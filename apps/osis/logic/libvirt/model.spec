[rootmodel:Image] @dbtype:osis
    """
    Libvirt images
    """
    prop:id str,,unique id of the image
    prop:gid int,,grid id
    prop:name str,,name of the image
    prop:description str,,extra description of the image
    prop:UNCPath str,,location of the image (uncpath like used in pylabs); includes the login/passwd info
    prop:size int,, size in MByte
    prop:type str,, dot separated list of independant terms known terms are: tar;gz;sso e.g. sso dump inn tar.gz format would be sso.tar.gz  (always in lcas)
    prop:status str,, status of image (always in upper case)
    prop:extra str,, extra data linked to the image
    
[rootmodel:Size] @dbtype:osis
    """
    Size is a combination of memory and cores.
    Because libvirt doesn't have a idea of size we created or own sizes store.
    """
    prop:id int, 0,id of the size
    prop:name str,,Public name of the size
    prop:memory int,, Memory in Mb
    prop:vcpus int,, Number of virtual cpus assigned to the machine
    prop:disk int,,disk size in GB

[rootmodel:ResourceProvider] @dbtype:osis
    prop:id str,,resourceprovider id is the uri of the compute node
    prop:gid int,, Grid id
    prop:cloudUnitType str,, (CU,VSU,SU,NU)
    prop:images list(str),,list of images ids supported by this resource
   
[rootmodel:Node] @dbtype:osis
    """
    Small local node configuariton
    """
    prop:id str,,id of the node
    prop:ipaddress str,,ipaddress of the node
    prop:macaddress str,,macaddress of the node
    prop:networkid int,,id of the network

[rootmodel:VNC] @dbtype:osis
    """
    Store vnc proxies
    """
    prop:id int, 0, id of vnc
    prop:gid int, 0, Grid id
    prop:url str,,Url of vnc proxy
