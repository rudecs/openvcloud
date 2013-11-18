'use strict';


var cloudscalers = angular.module('anonymous_cloudscalers', ['cloudscalers.services',
                                                   'cloudscalers.controllers'])

cloudscalers
    // Angular uses {{}} for data-binding. This operator will conflict with JumpScale macro syntax.
    // Use {[]} instead.
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[').endSymbol(']}');
    }]);

var cloudscalersControllers = angular.module('cloudscalers.controllers', ['ui.bootstrap', 'ui.slider', 'cloudscalers.machineServices', 'cloudscalers.directives']);


if(cloudspaceconfig.apibaseurl == ''){
	cloudscalersControllers.config(function($provide) {
    $provide.decorator('$httpBackend', angular.mock.e2e.$httpBackendDecorator)
  });
	cloudscalersControllers.run(defineApiStub);
};

// So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.value('alert', window.alert);