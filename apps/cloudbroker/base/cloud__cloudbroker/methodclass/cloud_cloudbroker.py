from JumpScale import j
from cloud_cloudbroker_osis import cloud_cloudbroker_osis
json = j.db.serializers.ujson


class cloud_cloudbroker(cloud_cloudbroker_osis):

    """
    iaas manager

    """

    def __init__(self):

        self._te = {}
        self.actorname = "cloudbroker"
        self.appname = "cloud"
        cloud_cloudbroker_osis.__init__(self)

        pass

    def cloudSpaceCreate(self, name, access, maxMemoryCapacity, maxDiskCapacity, **kwargs):
        """
        param:name name of space to create
        param:access list of ids of users which have full access to this space
        param:maxMemoryCapacity max size of memory in space (in GB)
        param:maxDiskCapacity max size of aggregated disks (in GB)
        result int

        """
        cs = self.models.cloudspace.new()
        cs.name = name
        for userid in access:
            ace = cs.new_acl()
            ace.userGroupId = userid
            ace.type = 'U'
            ace.right = 'RWD'
        cs.resourceLimits['CU'] = maxMemoryCapacity
        cs.resourceLimits['SU'] = maxDiskCapacity
        return self.models.cloudspace.set(cs.obj2dict())

    def machineAction(self, machineId, actiontype, **kwargs):
        """
        Perform a action on a machine, supported types are STOP, START, PAUSE, RESUME.
        param:machineId id of the machine
        param:actiontype type of the action(e.g stop, start, ...)
        result

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineAction")

    def machineGetConsole(self, machineId, **kwargs):
        """
        Get console access url
        param:machineId id of the machine
        result str

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineGetConsole")

    def machineAddDisk(self, machineId, diskName, description, size=10, type='B', **kwargs):
        """
        param:machineId id of machine
        param:diskName name of disk
        param:description optional description
        param:size size in GByte default=10
        param:type (B;D;T)  B=Boot;D=Data;T=Temp default=B
        result int
        """
        machine = self.model_vmachine_get(machineId)
        disk = self.models.disk.new()
        disk.name = diskName
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        diskid = self.model_disk_set(disk)
        machine['disks'].append(diskid)
        self.model_vmachine_set(machine)
        return diskid

    def machineBackup(self, machineId, backupName, **kwargs):
        """
        backup is in fact an export of the machine to a cloud system close to the IAAS system on which the machine is running
        param:machineId id of machine to backup
        param:backupName name of backup
        result int
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineBackup")

    def machineCopy(self, machineId, nameNew, **kwargs):
        """
        param:machineid int of machine to copy from (when active machine snapshot will happen first)
        param:nameNew name of machine to be created
        result int
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineCopy")

    def machineCreate(self, spaceId, name, description, nrCU=1, **kwargs):
        """
        param:spaceId id of space in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:nrCU amount of compute units default=1
        result bool
        """
        #TODO update this or remove
        args = {}
        args["spaceId"] = spaceId
        args["name"] = name
        args["description"] = description
        args["nrCU"] = nrCU
        return self._te["machineCreate"].execute4method(args, params={}, actor=self)

    def machineDelete(self, machineId, **kwargs):
        """
        Delete a machine
        param:machineId id of the machine
        """
        self.model_vmachine_delete(machineId)
        return True

    def machineCreate1Step(self, spaceId, name, description, nrCU=1, diskSize=10, **kwargs):
        """
        param:spaceId id of space in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:nrCU amount of compute units default=1
        param:diskSize size of disks in GByte default=10
        result bool
        """
        args = {}
        args["spaceId"] = spaceId
        args["name"] = name
        args["description"] = description
        args["nrCU"] = nrCU
        args["diskSize"] = diskSize
        return self._te["machineCreate1Step"].execute4method(args, params={}, actor=self)

    def machineDelDisk(self, machineId, diskId, **kwargs):
        """
        Delete a disk from machine
        param:machineId id of machine
        param:diskId id of disk to delete
        result bool
        """
        machine = self.model_vmachine_get(machineId)
        diskfound = diskId in machine['disks']
        if diskfound:
            machine['disks'].remove(diskId)
            self.model_vmachine_set(machine)
            self.model_disk_delete(diskId)
        return diskfound

    def machineExport(self, machineId, exportName, uncpath, **kwargs):
        """
        param:machineId id of machine to export
        param:exportName give name to export action
        param:uncpath unique path where to export machine to ()
        result int
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineExport")

    def machineGetDiskId(self, machineId, diskName, **kwargs):
        """
        Get disk id by name
        param:machineId id of machine
        param:diskName name of disk from which you would like to get the disk id which is unique for cloud
        result int
        """
        machine = self.model_vmachine_get(machineId)
        diskids = list()
        for diskid in machine['disks']:
            diskids.append({'term': {'id': diskid}})
        query = {'query':
                {'bool':
                {'must': [
                 {'term': {'name': diskName}}],
                    'should': diskids,
                    'minimum_should_match': 1
                         }
                 },
                 'fields': 'id'}
        results = self.model_disk_find(json.dumps(query))['result']
        ids = [res['fields']['id'] for res in results]
        return 0 if not ids else ids[0]

    def machineImport(self, name, uncpath, **kwargs):
        """
        param:name name of machine
        param:uncpath unique path where to import machine from ()
        result int
        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineImport")

    def machineList(self, spaceId, type, **kwargs):
        """
        param:spaceId id of space in which machine exists
        param:type when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT)
        result list
        """
        term = dict()
        if spaceId:
            term["cloudspaceId"] = spaceId
        if type:
            term["type"] = type
        query = {'query': {'term': term}, 'fields': ['id']}
        results = self.model_vmachine_find(json.dumps(query))['result']
        ids = [res['fields']['id'] for res in results]
        return ids
        # put your code here to implement this method

    def machineSnapshot(self, machineId, snapshotname, **kwargs):
        """
        param:machineId id of machine to snapshot
        param:snapshotname Optional name to give snapshot
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method machineSnapshot")

    def stackImportImages(self, stackId, **kwargs):
        """
        param:stackId id of stack to import from
        result int
        """
        return self.extensions.imp.stackImportImages(stackId)

    def stackImportSizes(self, stackId, **kwargs):
        """
        param:stackId id of stack to import
        result int
        """
        return self.extensions.imp.stackImportSizes(stackId)
