'use strict';


// Declare app level module which depends on filters, and services
var myApp = angular.module('myApp', ['myApp.filters', 'myApp.services', 'machineServices', 'myApp.directives', 'myApp.controllers'])

myApp
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/list', {templateUrl: 'partials/list', controller: 'BucketListCtrl'});
        $routeProvider.when('/new', {templateUrl: 'partials/new', controller: 'BucketNewCtrl'});
        $routeProvider.when('/edit/:bucketId', {templateUrl: 'partials/edit', controller: 'BucketEditCtrl'});
        $routeProvider.otherwise({redirectTo: '/list'});
    }])

    // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax. Here I configure
    // Angular to use {[]} instead.
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }]);


var myAppControllers = angular.module('myApp.controllers', ['ui.bootstrap', 'machineServices']);

if(cloudspaceconfig.apibaseurl == ''){
    myAppControllers.config(function($provide) {
       $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator)});
    myAppControllers.run(defineApiStub);


};