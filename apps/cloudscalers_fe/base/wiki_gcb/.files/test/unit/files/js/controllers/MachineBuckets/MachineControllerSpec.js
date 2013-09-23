describe("Machine bucket controller tests", function(){
	var scope, ctrl, user, machine, Machine;
	var machinelist = [
		{status: "RUNNING", hostname: "jenkins.cloudscalers.com", "description": "JS Webserver", "name": "CloudScalers Jenkins", "nics": [], "sizeId": 0, "imageId": 0, "id": 0},
		{status: "HALTED", hostname: "cloudbroker.cloudscalers.com", "description": "CloudScalers CloudBroker",  "name": "CloudBroker", "nics": [], "sizeId": 0, "imageId": 1, "id": 1}];

	beforeEach(module('myApp'));
	
	beforeEach(inject(function($rootScope) {
		machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		scope = $rootScope.$new();
	}));

	
	describe("machine list", function() {
		beforeEach(inject(function($controller){
			machine.list.andReturn(machinelist);
		 	ctrl = $controller('MachineController', {$scope : scope, Machine : machine});
		}));

	 	it("provides a list of machines on the service", function() {
			expect(scope.buckets.length).toBe(2);
			expect(scope.buckets[0].hostname).toBe("jenkins.cloudscalers.com");
			expect(scope.buckets[1].hostname).toBe("cloudbroker.cloudscalers.com");
		});

		xit('view the number of data locations of each buckets', function() {
			expect(scope.numOfDataLocations).toBeDefined();
			expect(scope.numOfDataLocations(scope.buckets[0])).toBeDefined();
		});
	});

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

