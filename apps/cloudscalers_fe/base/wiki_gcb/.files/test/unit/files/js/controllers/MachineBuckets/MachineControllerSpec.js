describe("Machine bucket controller tests", function(){
	var scope, ctrl, machine, q, $httpBackend;
	var machinelist = [
		{status: "RUNNING", hostname: "jenkins.cloudscalers.com", "description": "JS Webserver", "name": "CloudScalers Jenkins", "nics": [], "sizeId": 0, "imageId": 0, "id": 0},
		{status: "HALTED", hostname: "cloudbroker.cloudscalers.com", "description": "CloudScalers CloudBroker",  "name": "CloudBroker", "nics": [], "sizeId": 0, "imageId": 1, "id": 1}];

	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope, $q, _$httpBackend_) {
		machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		scope = $rootScope.$new();
		q = $q;
		$httpBackend = _$httpBackend_;
        defineUnitApiStub($httpBackend);
	}));

	
	describe("machine list", function() {
		var listdefer;
		beforeEach(inject(function($controller) {
			listdefer = q.defer();
			machine.list.andReturn(listdefer.promise);
		 	ctrl = $controller('MachineController', {$scope : scope, Machine : machine});
		}));

	 	it("provides a list of machines on the scope", function() {
			scope.currentSpace = {id:1,name:'teset'};
	 		scope.$digest();
	 		listdefer.resolve(machinelist);
	 		scope.$digest();
			expect(scope.machines.length).toBe(2);
			expect(scope.machines[0].hostname).toBe("jenkins.cloudscalers.com");
			expect(scope.machines[1].hostname).toBe("cloudbroker.cloudscalers.com");
		});
	});

});

