describe("Machine bucket creation controller tests", function(){
	var scope, ctrl, machine, $location, confirm;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		Machine = {
			list : jasmine.createSpy('list'), 
			create: jasmine.createSpy('create'), 
			get: jasmine.createSpy('get'), 
			delete: jasmine.createSpy('delete'), 
		};
		scope = $rootScope.$new();
		confirm = jasmine.createSpy('confirm');
	}));


	describe("Edit machine bucket", function() {
		beforeEach(inject(function($controller, _$location_) {
			Machine.get.andReturn({id: 13, name: 'Machine 13'});
			$location = _$location_;
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
	});
});

