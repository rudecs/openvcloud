describe("Machine bucket controller tests", function(){
	var scope, ctrl, user;
	
	beforeEach(module('myApp'));
	
	beforeEach(inject(function($rootScope) {

		machine = {list : jasmine.createSpy()};

		scope = $rootScope.$new();
	}));

	var machinelist = {0:{status: "RUNNING", hostname: "jenkins.cloudscalers.com", "description": "JS Webserver", "name": "CloudScalers Jenkins", "nics": [], "sizeId": 0, "imageId": 0, "id": 0},
			1:{"status": "HALTED", hostname: "cloudbroker.cloudscalers.com", "description": "CloudScalers CloudBroker",  "name": "CloudBroker", "nics": [], "sizeId": 0, "imageId": 1, "id": 1}};

	
	it("provides a list of machines on the model", function(){
		machine.list.andReturn(machinelist);
		
		inject(function($controller){
			ctrl = $controller('MachineController', {$scope : scope, Machine : machine});
		}); 
		
		expect(scope.buckets[0].hostname).toBe("jenkins.cloudscalers.com");
		expect(scope.buckets[1].hostname).toBe("cloudbroker.cloudscalers.com");
		
	});
	
});