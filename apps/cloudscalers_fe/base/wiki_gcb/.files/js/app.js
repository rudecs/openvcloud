'use strict';


// Declare app level module which depends on filters, and services
var cloudscalers = angular.module('cloudscalers', ['cloudscalers.filters', 'cloudscalers.services', 'machineServices', 'cloudscalers.directives', 'cloudscalers.controllers'])

cloudscalers
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/list', {templateUrl: 'partials/list', controller: 'MachineController'});
        $routeProvider.when('/new', {templateUrl: 'partials/new', controller: 'BucketNewCtrl'});
        $routeProvider.when('/edit/:bucketId', {templateUrl: 'partials/edit', controller: 'BucketEditCtrl'});
        $routeProvider.otherwise({redirectTo: '/list'});
    }])

    // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax. Here I configure
    // Angular to use {[]} instead.
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }]);


var cloudscalersControllers = angular.module('cloudscalers.controllers', ['ui.bootstrap', 'machineServices']);

if(cloudspaceconfig.apibaseurl == ''){
	cloudscalersControllers.config(function($provide) {
       $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator)});
	cloudscalersControllers.run(defineApiStub);


};