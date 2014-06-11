
angular.module('cloudscalers.services')

	.factory('User', function ($http, $q, SessionData) {
    	return {
            updatePassword: function(username, oldPassword, newPassword) {
                return $http.get(cloudspaceconfig.apibaseurl + '/users/updatePassword?username=' + username + '&oldPassword=' + oldPassword +
                    '&newPassword=' + newPassword
                    ).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            }
        };
    });
