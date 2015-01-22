var cloudscalers = angular.module('cloudscalers',[
                                                  'cloudscalers.services',
                                                  'cloudscalers.controllers',
                                                  'ngRoute']);

var cloudscalersServices = angular.module('cloudscalers.services',['ng'])
	.config(['$httpProvider',function($httpProvider) {
		$httpProvider.interceptors.push('authenticationInterceptor');
	}]);

var cloudscalersControllers = angular.module('cloudscalers.controllers', ['ui.bootstrap', 'ui.slider', 'cloudscalers.services', 'cloudscalers.directives']);


//So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.value('alert', window.alert);