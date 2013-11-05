describe("Machine bucket editing controller", function(){
	var scope, ctrl, machine, $location, $sce, confirm, $modal, q, $httpBackend;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope, $controller, _$location_, $q, _$httpBackend_) {
		scope = $rootScope.$new();
		q = $q;
		$location = _$location_;
		$httpBackend = _$httpBackend_;
		defineUnitApiStub($httpBackend);

		confirm = jasmine.createSpy('confirm');
		$modal = {
				open: jasmine.createSpy('$modal.open')
		};
		
		Machine = {
			list : jasmine.createSpy('list'), 
			create: jasmine.createSpy('create'), 
			get: jasmine.createSpy('get'), 
			delete: jasmine.createSpy('delete'), 
			createSnapshot: jasmine.createSpy('createSnapshot'), 
			listSnapshots: jasmine.createSpy('listSnapshots')
		};
		Machine.get.andReturn({id: 13, name: 'Machine 13'});
		Machine.listSnapshots.andReturn([{id: 10, name: 'Snapshot 1'}]);
	 	
	 	ctrl = $controller('MachineEditController', {
	 		$scope : scope, 
	 		$routeParams: {machineId: 13},
	 		$location: $location,
	 		Machine : Machine, 
	 		confirm: confirm,
	 		$modal:$modal
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
 	    	var deffered;
 	    	
 	    	deferred = q.defer();
 	    	
 	    	$modal.open.andReturn({result:deferred.promise});
 	    	
 	    	scope.createSnapshot();
 	    	
 	    	expect(Machine.createSnapshot).not.toHaveBeenCalled();
 	    	
 	    	scope.$apply(function() {	
 	    		deferred.resolve(newSnapshotName);
 	    	});
 	    	
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

