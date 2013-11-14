describe("Create Machine bucket controller tests", function(){
	var machinescope, scope, ctrl, Machine, q;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope, $q) {
		Machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		Image = {list: jasmine.createSpy('list')};
		Size = {list: jasmine.createSpy('list')};
		machinescope = $rootScope.$new();
		scope = machinescope.$new();
		q = $q;
	}));

	
	describe("New machine bucket", function() {
 		beforeEach(inject(function($controller){
		 	Machine.create.andReturn(q.defer().promise);
		 	machinescope.sizes = [{id: 1, name: 'Size 1'}, {id: 2, name: 'Size 2'}];
		 	machinescope.images = [{id: 1, name: 'Image 1'}, {id: 2, name: 'Image 2'}, {id: 3, name: 'Image 3'}];
		 	
		 	ctrl = $controller('MachineCreationController', {$scope : scope, Machine : Machine });
		 	
		 	scope.machine = {
	            cloudspaceId: 10,
	            name: 'Test machine 1',
	            description: 'Test machine 1 description',
	            sizeId: 1,
	            imageId: 2,
	            disksize: 3,
	            archive: 4,
	            region: 5,
	            replication: 6
	        };
			
			scope.saveNewMachine();
		}));

		it('valid machine definition & can be saved', function() {
			expect(scope.isValid()).toBeTruthy();
		});

		it('save calls the service with correct parameters', function() {
			expect(Machine.create).toHaveBeenCalledWith(10, "Test machine 1", "Test machine 1 description", 1, 2, 3, 4, 5, 6);
		});
	});
	
	describe("default selection", function(){
		it('minimal size', function(){
				machinescope.sizes = [{id:3,vcpus:3}, {id:1,vcpus:1}];
				inject(function($controller){
					ctrl = $controller('MachineCreationController', {$scope : scope, Machine : Machine});
				});
				scope.$digest();
				expect(scope.machine.sizeId).toBe(1);
		});
	});
			

});

