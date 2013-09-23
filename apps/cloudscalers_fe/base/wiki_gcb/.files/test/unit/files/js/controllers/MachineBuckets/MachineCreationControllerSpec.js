describe("Machine bucket controller tests", function(){
	var scope, ctrl, machine;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		scope = $rootScope.$new();
	}));

	
	describe("New machine bucket", function() {
 		beforeEach(inject(function($controller){
		 	machine.create.andReturn(10);
		 	ctrl = $controller('MachineCreationController', {$scope : scope, Machine : machine});
		 	
		 	scope.newMachine = {
	            cloudspaceId: 10,
	            name: 'Test machine 1',
	            description: 'Test machine 1 description',
	            sizeId: 1,
	            imageId: 2
	        };
			
			scope.saveNewMachine();
		}));

		it('called the service with correct parameters', function() {
			expect(machine.create).toHaveBeenCalledWith(10, "Test machine 1", "Test machine 1 description", 1, 2);
		});
	});

});

