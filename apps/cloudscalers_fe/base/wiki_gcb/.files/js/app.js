'use strict';


// Declare app level module which depends on filters, and services
var cloudscalers = angular.module('cloudscalers', ['cloudscalers.services',
                                                   'cloudscalers.controllers',
                                                   'ngRoute'])

cloudscalers
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/list', {templateUrl: 'partials/list'});
        $routeProvider.when('/new', {templateUrl: 'partials/new', controller: 'MachineCreationController'});
        $routeProvider.when('/edit/:machineId/:activeTab?', {templateUrl: 'partials/edit', controller: 'MachineEditController'});
        $routeProvider.otherwise({redirectTo: '/list'});
    }])

    // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax.
    // Use {[]} instead.
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }]);

var cloudscalersServices = angular.module('cloudscalers.services',['ng'])
	.config(['$httpProvider',function($httpProvider) {
		$httpProvider.interceptors.push('authenticationInterceptor');
	}]);


var cloudscalersControllers = angular.module('cloudscalers.controllers', ['ui.bootstrap', 'ui.slider', 'cloudscalers.services', 'cloudscalers.directives']);

if(cloudspaceconfig.apibaseurl == ''){
	cloudscalersControllers.config(function($provide) {
    $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator)
  });
	cloudscalersControllers.run(defineApiStub);


};

// So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.value('alert', window.alert);
