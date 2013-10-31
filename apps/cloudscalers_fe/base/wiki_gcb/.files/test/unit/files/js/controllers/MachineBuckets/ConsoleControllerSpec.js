describe("Machine console controller tests", function(){
	var scope, ctrl, machine;
	
	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		machine = {getConsoleUrl : jasmine.createSpy('getConsoleUrl') };
		scope = $rootScope.$new();
	}));

	
	describe("connectioninfo ", function() {
		beforeEach(inject(function($controller) {
			machine.getConsoleUrl.andReturn({});
			var routeparams = {machineId: 7};
		 	ctrl = $controller('ConsoleController', {$scope : scope, $routeparams : routeparams, Machine : machine});
		}));

		it("connectioninfo correctly created from the consoleUrl", function() {
		//	expect(machine.getConsoleUrl).toHaveBeenCalledWith(7);
			
			expect(scope.novnc_connectioninfo).not.toBe(null);
			
		});
	});

});

