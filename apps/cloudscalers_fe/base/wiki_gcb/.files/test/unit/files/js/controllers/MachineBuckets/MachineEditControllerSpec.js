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

});

