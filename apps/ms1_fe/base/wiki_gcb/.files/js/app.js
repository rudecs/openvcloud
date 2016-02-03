'use strict';


// Declare app level module which depends on filters, and services
var cloudscalers = angular.module('cloudscalers', ['cloudscalers.services',
                                                   'cloudscalers.controllers',
                                                   'ngRoute',
                                                   'angular-szn-autocomplete',
                                                   'ui.bootstrap'])

cloudscalers
    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/list', {templateUrl: 'pages/list'});
        $routeProvider.when('/new', {templateUrl: 'pages/new', controller: 'MachineCreationController'});
        $routeProvider.when('/edit/:machineId/:activeTab?', {templateUrl: 'pages/details', controller: 'MachineEditController'});
        $routeProvider.otherwise({redirectTo: '/list'});
    }])

    .config(['$interpolateProvider','$compileProvider', function($interpolateProvider,$compileProvider) {
        // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax.
        // Use {[]} instead.
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
        //Accept bitcoin and litecoin urls
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|bitcoin|litecoin):/);
    }]);

var cloudscalersServices = angular.module('cloudscalers.services',['ng'])
    .config(['$httpProvider',function($httpProvider) {
        $httpProvider.interceptors.push('authenticationInterceptor');
        //initialize get if not there
        if (!$httpProvider.defaults.headers.get) {
            $httpProvider.defaults.headers.get = {};
        }
        //disable IE ajax request caching
        $httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
    }]);


var cloudscalersControllers = angular.module('cloudscalers.controllers', ['ui.slider', 'cloudscalers.services', 'cloudscalers.directives', 'angular-tour', 'ipCookie']);

if(cloudspaceconfig.apibaseurl == ''){
    cloudscalersControllers.config(function($provide) {
    $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator)
  });
    cloudscalersControllers.run(defineApiStub);


};

// So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.factory('$alert', function($modal) {
    return function(message) {
        var ModalInstanceCtrl = function ($scope, $modalInstance) {
            $scope.message = message.replace('\n', '<br>');
            $scope.ok = function () {
                $modalInstance.close();
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        };

        var modalInstance = $modal.open({
            templateUrl: 'myModalContent.html',
            controller: ModalInstanceCtrl,
            resolve: {}
        });
    };
});
cloudscalers.factory('$ErrorResponseAlert',function($alert){
    return function(reason) {
        if (reason.status == 500 || reason.status == 502 || reason.status == 504 || reason.data == null){
            $alert("An unexpected error has occurred");
        }
        else{
            var message = "";
            try {
                message = JSON.parse(reason.data);
                if (typeof message !== 'string'){
                    message = reason.data;
                }
            } catch (e) {
                message = reason.data;
                //data is not JSON
            }
            $alert(message);
        }
    }
});


cloudscalers.run(function($templateCache) {
    $templateCache.put('autocomplete-result-template.html', 
        '<ul ng-show="show" class="szn-autocomplete-results"> ' +
            '<li ' +
                'szn-autocomplete-result ' +
                'ng-repeat="result in results" ' +
                'ng-class="{selected: highlightIndex == $index}" ' +
                'ng-show="results.length"> ' +
                '<div class="text-left"> ' +
                    '<img class="gravatar" ng-show="result.gravatarurl" ng-src="{[result.gravatarurl]}" /> ' +
                    '<span ng-show="!result.validEmail" view-as-html="result.value | sznAutocompleteBoldMatch:query"></span> ' +

                    '<span ng-show="result.validEmail">Invite: <strong>{[result.value]}</strong></span> ' +
                '</div> ' +
            '</li> ' +
        '</ul>'
    );
});