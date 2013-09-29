describe("Machine bucket controller tests", function(){
	var scope, ctrl, Machine;

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		Machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		Image = {list: jasmine.createSpy('list')};
		Size = {list: jasmine.createSpy('list')};
		scope = $rootScope.$new();
	}));

	
	describe("New machine bucket", function() {
 		beforeEach(inject(function($controller){
		 	Machine.create.andReturn(10);
		 	Size.list.andReturn([{id: 1, name: 'Size 1'}, {id: 2, name: 'Size 2'}]);
		 	Image.list.andReturn([{id: 1, name: 'Image 1'}, {id: 2, name: 'Image 2'}, {id: 3, name: 'Image 3'}]);

		 	ctrl = $controller('MachineCreationController', {$scope : scope, Machine : Machine, Image: Image, Size: Size});
		 	
		 	scope.newMachine = {
	            cloudspaceId: 10,
	            name: 'Test machine 1',
	            description: 'Test machine 1 description',
	            sizeId: 1,
	            imageId: 2
	        };
			
			scope.saveNewMachine();
		}));

		it('is valid machine definition & can be saved', function() {
			expect(scope.isValid()).toBeTruthy();
		});

		it('retrieved list of sizes', function() {
			expect(Size.list).toHaveBeenCalledWith();
		});

		it('retrieved list of images', function() {
			expect(Image.list).toHaveBeenCalledWith();
		});

		it('called the service with correct parameters', function() {
			expect(Machine.create).toHaveBeenCalledWith(10, "Test machine 1", "Test machine 1 description", 1, 2);
		});
	});

});

