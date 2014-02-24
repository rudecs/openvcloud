
[rootmodel:BillingStatement] @dbtype:osis
	"""
	Cloud usage that should be billed for an account
	"""
	prop:id str,,
	prop:accountId int,,
	prop:lastupdatedTime int,,
	prop:cloudspaces list(CloudSpaceUsage),,
	prop:totalCost float,,
	prop:fromTime int,,
	prop:untilTime int,,

[rootmodel:CloudSpaceUsage] @dbtype:osis
    """
    Usage that should be billed for a cloudspace
    """
    prop:cloudspaceId int,,
    prop:name str,,name as given by customer
	prop:machines list(VMachine),,
    prop:totalCost float,,
    prop:creationTime int,, epoch time of creation, in seconds
    prop:deletionTime int,, epoch time of destruction, in seconds

[model:VMachine] @dbtype:osis
    """
    Machine account on the virtual machine
    """
	prop:machineId int,,
    prop:name str,,name as given by customer
    prop:sizeId int,,id of size used by machine, size is the cloudbroker size.
    prop:imageId int,,id of image used to create machine
    prop:disks list(int),,List of id of Disk objects
    prop:status str,,status of the vm (HALTED;INIT;RUNNING;TODELETE;SNAPSHOT;EXPORT;DESTROYED)
    prop:hostName str,,hostname of the machine as specified by OS; is name in case no hostname is provided
    prop:cpus int,1,number of cpu assigned to the vm
    prop:cloudspaceId int,,id of space which holds this vmachine
    prop:networkGatewayIPv4 str,,IP address of the gateway for this vmachine
    prop:creationTime int,, epoch time of creation, in seconds
    prop:deletionTime int,, epoch time of destruction, in seconds