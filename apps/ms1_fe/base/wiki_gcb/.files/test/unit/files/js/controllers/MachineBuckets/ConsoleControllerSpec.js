describe("Machine console controller tests", function(){
	var scope, ctrl, machine;
	
	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		machine = {getConsoleUrl : jasmine.createSpy('getConsoleUrl') };
		scope = $rootScope.$new();
	}));

	
	describe("connectioninfo ", function() {
		
		it("connectioninfo correctly created from the consoleUrl", function() {
			var consoleUrlResult = {};
			machine.getConsoleUrl.andReturn(consoleUrlResult);
			var routeparams = {machineId: 7};
			inject(function($controller) {
				ctrl = $controller('ConsoleController', {$scope : scope, $routeparams : routeparams, Machine : machine});		
			});
		 	
		 	consoleUrlResult.url = "http://test.com:8900/blabla/aut0_vnc?token=mytoken";
		 	scope.$digest();
		 	
			expect(scope.novncConnectionInfo).not.toBe(null);
			expect(scope.novncConnectionInfo.host).toBe('test.com');
			expect(scope.novncConnectionInfo.path).toBe('websockify?token=mytoken');
			expect(scope.novncConnectionInfo.port).toBe('8900');
			
		});
		

		it("no port in the returned url, connectioninfo port taken from protocol", function() {
			var consoleUrlResult = {};
			machine.getConsoleUrl.andReturn(consoleUrlResult);
			var routeparams = {machineId: 7};
			inject(function($controller) {
				ctrl = $controller('ConsoleController', {$scope : scope, $routeparams : routeparams, Machine : machine});		
			});
		 	
		 	consoleUrlResult.url = "http://test.com/blabla/aut0_vnc?token=mytoken";
		 	scope.$digest();
		 	
			expect(scope.novncConnectionInfo).not.toBe(null);
			expect(scope.novncConnectionInfo.host).toBe('test.com');
			expect(scope.novncConnectionInfo.path).toBe('websockify?token=mytoken');
			expect(scope.novncConnectionInfo.port).toBe('80');
			
		});
		
	});

});

