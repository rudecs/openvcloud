[actor] @dbtype:mem,osis
    """
    iaas manager
    """    

    method:machineCreate1Step @tasklets
        """     
        """
        var:spaceId int,,id of space in which we want to create a machine
        var:name str,,name of machine
        var:description str,,optional description
        var:nrCU int,1,amount of compute units
        var:diskSize int,10,size of disks in GByte
        result:bool    


    method:machineCreate @tasklets
        """     
        """
        var:spaceId int,,id of space in which we want to create a machine
        var:name str,,name of machine
        var:description str,,optional description
        var:nrCU int,1,amount of compute units
        result:bool

    method:machineAction
        """
        Perform a action on a machine, supported types are STOP, START, SUSPEND, RESUME.

        """
        var:machineId int,, id of the machine
        var:actiontype str,, type of the action(e.g stop, start, ...)
        result:bool

    method:machineGetConsole
        """
        Get console access url
        """
        var:machineId int,, id of the machine
        result:str

    method:machineDelete
        """
        Delete a machine
        """
        var:machineId int,, id of the machine
        result: bool

    method:machineAddDisk
        """     
        """
        var:machineId int,,id of machine
        var:diskName str,,name of disk
        var:description str,,optional description
        var:size int,10,size in GByte
        var:type str,B, (B;D;T)  B=Boot;D=Data;T=Temp
        result:int

    method:machineDelDisk
        """     
        Delete a disk from machine
        """
        var:machineId int,, id of machine       
        var:diskId int,,id of disk to delete
        result:bool    

    method:machineGetDiskId
        """     
        Get disk id by name
        """
        var:machineId int,,id of machine        
        var:diskName str,,name of disk from which you would like to get the disk id which is unique for cloud
        result:int

    method:machineExport
        """     
        """
        var:machineId str,,id of machine to export
        var:exportName str,,give name to export action
        var:uncpath str,,unique path where to export machine to () #@todo give example ftp
        result:int  #returns id of new machine create in system which remembers where export happened to

    method:machineImport
        """     
        """
        var:name str,,name of machine
        var:uncpath str,,unique path where to import machine from () #@todo give example ftp
        result:int  #returns id of new machine create in system which remembers where export happened to

    method:machineSnapshot
        """
        """
        var:machineId int,,id of machine to snapshot
        var:snapshotname str,, Optional name to give snapshot
        result:int #returns id of new machine which gets created when snapshot was successfull

    method:machineCopy
        """     
        """
        var:machineId int,,int of machine to copy from (when active machine snapshot will happen first)
        var:nameNew str,,name of machine to be created
        result:int  #returns id of new machine created

    method:machineBackup
        """     
        backup is in fact an export of the machine to a cloud system close to the IAAS system on which the machine is running
        """
        var:machineId str,,id of machine to backup
        var:backupName str,,name of backup
        result:int  #returns id of new machine created

    method:machineList
        """
        """
        var:spaceId int,,id of space in which machine exists
        var:type str,,when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT)
        result:list #return nice json object with lots of info from machines in space

    method:cloudSpaceCreate
        """     
        """
        var:name str,,name of space to create
        var:access list,,list of ids of users which have full access to this space
        var:maxMemoryCapacity int,,max size of memory in space (in GB)
        var:maxDiskCapacity int,,max size of aggregated disks (in GB)
        result:int  #returns id of space created


    method:stackImportSizes
        """     
        """
        var:stackId int,,id of stack to import
        result:int  #returns number of sizes that where updated


    method:stackImportImages
        """     
        """
        var:stackId int,,id of stack to import from
        result:int  #returns number of images that where updated
