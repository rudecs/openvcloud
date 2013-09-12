[actor] @dbtype:mem,osis
	"""
	API Actor api, this actor is the final api a enduser uses to manage his resources
	"""    

    method:create
		"""
		Create a machine based on the available sizes, in a certain space.
		The user needs write access rights on the space.	
		"""
		var:cloudspaceId int,,id of space in which we want to create a machine
		var:name str,,name of machine
		var:description str,,optional description
		var:sizeId int,1,id of the specific size
		var:imageId int,,id of the specific image
		result:bool    


	method:list
		"""
		List the deployed machines in a space. Filtering based on status is possible.
		"""
		var:cloudspaceId int,,id of space in which machine exists @tags: optional 
		var:type str,,when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT) @tags: optional 
		result:list 

	method:get
		"""
		Get information from a certain object.
		This contains all information about the machine.
		"""
		var:machineId int,, id of machine
		result: bool

    method:delete
	    """
	    Delete a machine
	    """
	    var:machineId int,, id of the machine
	    result: bool

	method:update
	    """
	    Change basic properties of a machine.
	    Name, description can be changed with this action.
	    """
	    var:machineId int,, id of the machine
	    var:name str,, name of the machine
	    var:description str,, description of the machine
	    var:size int,,size of the machine in CU

	method:action
	    """
	    Perform a action on a machine, supported types are STOP, START, SUSPEND, RESUME.
	    """
	    var:machineId int,, id of the machine
	    var:actiontype str,, type of the action(e.g stop, start, ...)
	    result:bool

    method:addDisk
		"""
		Add a disk to a machine
		"""
		var:machineId int,,id of machine
		var:diskName str,,name of disk
		var:description str,,optional description
		var:size int,10,size in GByte
		var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
		result:int

    method:delDisk
		"""		
        Delete a disk from machine
		"""
		var:machineId int,, id of machine		
		var:diskId int,,id of disk to delete
		result:bool    

	method:exporttoremote
		"""		
		"""
		var:machineId str,,id of machine to export
		var:exportName str,,give name to export action
		var:uncpath str,,unique path where to export machine to () #@todo give example ftp
		result:int  #returns id of new machine create in system which remembers where export happened to

	method:importtoremote
		"""		
		"""
		var:name str,,name of machine
		var:uncpath str,,unique path where to import machine from () #@todo give example ftp
		result:int  #returns id of new machine create in system which remembers where export happened to

	method:snapshot
		"""
		"""
		var:machineId int,,id of machine to snapshot
        var:snapshotname str,, Optional name to give snapshot
		result:int #returns id of new machine which gets created when snapshot was successfull

	method:listSnapshots
		"""
		List the snapshot of a machine
        """
	    var:machineId int,, id of the machine
		result:list 


	method:deleteSnapshot
		"""
		Delete a snapshot of a machine
        """
	    var:machineId int,, id of the machine
	    var:name str,, name of the snapshot to delete
		result:str


	method:rollbackSnapshot
		"""
		Rollback a snapshot of a machine
        """
	    var:machineId int,, id of the machine
	    var:name str,, name of the snapshot to rollback
		result:str

	method:backup
		"""		
		backup is in fact an export of the machine to a cloud system close to the IAAS system on which the machine is running
		"""
		var:machineId str,,id of machine to backup
		var:backupName str,,name of backup
		result:int  #returns id of new machine created

