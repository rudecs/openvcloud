
angular.module('cloudscalers.AccountServices', ['ng','cloudscalers.SessionServices'])

	.config(['$httpProvider',function($httpProvider) {
        $httpProvider.interceptors.push('authenticationInterceptor');
	}])
    .factory('Account',function ($http, $q) {
    	
    	
    	
    });