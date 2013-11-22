
angular.module('cloudscalers.AccountServices', ['ng','cloudscalers.SessionServices'])

	.config(['$httpProvider',function($httpProvider) {
        $httpProvider.interceptors.push('authenticationInterceptor');
	}])
    .factory('Account',function ($http, $q) {
    	return {
            list: function() {
                var accounts = $http.get(cloudspaceconfig.apibaseurl + '/accounts/list');
                var cloudspaces = $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/list');

                return $q.all([accounts, cloudspaces]).then(function(promises) {
                            var accounts = promises[0].data;
                            var cloudspaces = promises[1].data;
                            var cloudspacesGroups = _.groupBy(cloudspaces, 'account');
                            return _.map(accounts, function(account) { 
                                account.cloudspaces = cloudspacesGroups[account.id]; 
                                return account;
                            });
                    });
            }
        };
    });