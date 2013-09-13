[rootmodel:Image] @dbtype:osis
    """
    Libvirt images
    """
    prop:id int,,
    prop:name str,,name of the image
    prop:description str,,extra description of the image
    prop:UNCPath str,,location of the image (uncpath like used in pylabs); includes the login/passwd info
    prop:size int,, size in MByte
    prop:type str,, dot separated list of independant terms known terms are: tar;gz;sso e.g. sso dump inn tar.gz format would be sso.tar.gz  (always in lcas)
    prop:referenceId str,,Name of the image on stack


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
