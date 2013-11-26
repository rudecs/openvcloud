
angular.module('cloudscalers.services')

	.factory('Account', function ($http, $q, SessionData) {
    	return {
            list: function() {
                return $http.get(cloudspaceconfig.apibaseurl + '/accounts/list').then(
                		function(result) {
                            return result.data;
                            var cloudspaces = promises[1].data;
                    });
            },
            current: function() {
                return SessionData.getAccount();
            },
            setCurrent: function(account) {
                SessionData.setAccount(account);
            }
        };
    });