describe("Machine bucket editing controller", function(){
	var scope, ctrl, machine, $location, $sce, confirm;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope, $controller, _$location_, _$sce_) {
		scope = $rootScope.$new();
		$sce = _$sce_;
		$location = _$location_;

		confirm = jasmine.createSpy('confirm');
		
		Machine = {
			list : jasmine.createSpy('list'), 
			create: jasmine.createSpy('create'), 
			get: jasmine.createSpy('get'), 
			delete: jasmine.createSpy('delete'), 
			createSnapshot: jasmine.createSpy('delete'), 
			listSnapshots: jasmine.createSpy('listSnapshots'),
			getConsoleUrl: jasmine.createSpy('getConsoleUrl')
		};
		Machine.get.andReturn({id: 13, name: 'Machine 13'});
		Machine.listSnapshots.andReturn([{id: 10, name: 'Snapshot 1'}]);
		Machine.getConsoleUrl.andReturn({url: $sce.trustAsResourceUrl('http://www.yahoo.com')});
	 	
	 	ctrl = $controller('MachineEditController', {
	 		$scope : scope, 
	 		$routeParams: {machineId: 13},
	 		$location: $location,
	 		Machine : Machine, 
	 		confirm: confirm 
	 	});
	}));

 	it("retrieve the given bucket", function() {
		expect(Machine.get).toHaveBeenCalledWith(13);
 		expect(scope.machine.id).toBe(13);
 	});

 	describe("deleting a machine", function() {
 	  	it('confirming the warning will delete the machine', inject(function($location) {
 	  		confirm.andReturn(true);
 	  		
 	  		scope.destroy();
 	  		
 	  		expect(confirm).toHaveBeenCalled();
 	  		expect(Machine.delete).toHaveBeenCalledWith(13);
 	  		expect($location.url()).toEqual('/list');
 	  	}));

 	  	it('rejecting the warning will not delete the machine', inject(function($location) {
 	  		spyOn($location, 'path').andCallThrough();
 	  		confirm.andReturn(false);
 	  		
 	  		scope.destroy();
 	  		
 	  		expect(confirm).toHaveBeenCalled();
 	  		expect(Machine.delete).not.toHaveBeenCalled();
 	  		expect($location.path).not.toHaveBeenCalled();
 	  	}));
 	});

 	describe("Snapshots", function() {
 	  it("can create snapshots", function() {
 	    	var newSnapshotName = '13_snapshot_' + Math.random();
 	    	scope.newSnapshotName = newSnapshotName;
 	    	scope.createSnapshot();

 	    	expect(Machine.createSnapshot).toHaveBeenCalledWith(13, newSnapshotName);
 	  });

 	  it('lists snapshots for this machine', function() {
 	  	expect(Machine.listSnapshots).toHaveBeenCalledWith(13);
 	  	expect(scope.snapshots).toBeDefined();
 	  	expect(scope.snapshots.length).toBeDefined();
 	  	expect(scope.snapshots.length).toBe(1);
 	  });
 	});
	
});

