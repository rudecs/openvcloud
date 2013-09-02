'use strict';


// Declare app level module which depends on filters, and services
angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers'])
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

jQuery(function() {
// UI stuff which are not related to angular
// Popups
    $('.popup-show').on('click', function(e) {
        e.preventDefault();
        $($(this).attr('href')).toggle('fast');
    });
    $('.popup-background').on('click', function() {
        $(this).parent().hide();
    });
    $('.popup-content').on('click', function(e) {
        e.stopPropagation();
    });
});