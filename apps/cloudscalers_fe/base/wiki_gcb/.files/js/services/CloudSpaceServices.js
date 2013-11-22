
angular.module('cloudscalers.CloudSpaceServices', ['ng','cloudscalers.SessionServices'])

	.config(['$httpProvider',function($httpProvider) {
        $httpProvider.interceptors.push('authenticationInterceptor');
	}])
    .factory('CloudSpace',function ($http, $q) {
    	return {
            list: function() {
            	 return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/list').then(
            			 function(result){
            				 return result.data;
            			 },
            			 function(reason){
            				 $q.defer(reason);
            			 }
            			 );

            }
        };
    });