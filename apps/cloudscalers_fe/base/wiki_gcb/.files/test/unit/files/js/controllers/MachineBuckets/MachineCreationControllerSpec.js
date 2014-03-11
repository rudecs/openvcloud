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
			machinescope.currentSpace = {id:1,name:'teset'};
			
		 	ctrl = $controller('MachineCreationController', {$scope : scope, Machine : Machine });
		 	
		 	scope.machine = {
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
	});		

});

