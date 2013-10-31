describe("Machine console controller tests", function(){
	var scope, ctrl, machine;
	
	beforeEach(module('cloudscalers'));
	
	beforeEach(inject(function($rootScope) {
		machine = {list : jasmine.createSpy('list'), create: jasmine.createSpy('create'), get: jasmine.createSpy('get') };
		scope = $rootScope.$new();
	}));

	
	describe("connectioninfo ", function() {
		beforeEach(inject(function($controller) {
			machine.list.andReturn({});
		 	ctrl = $controller('ConsoleController', {$scope : scope, Machine : machine});
		}));

	 	
	});

});

