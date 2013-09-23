describe("Machine bucket creation controller tests", function(){
	var scope, ctrl, machine;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		scope = $rootScope.$new();
	}));


	describe("Edit machine bucket", function() {
		beforeEach(inject(function($controller) {
			machine.get.andReturn({id: 13, name: 'Machine 13'});
		 	ctrl = $controller('MachineEditController', {$scope : scope, $routeParams: {machineId: 13}, Machine : machine});
		}));

	 	it("retrieve the given bucket", function() {
			expect(machine.get).toHaveBeenCalledWith(13);
	 		expect(scope.machine.id).toBe(13);
	 	})
	});
});

