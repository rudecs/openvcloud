
angular.module('cloudscalers.services')

	.factory('LocationsService', function ($http, $q) {
    	return {
            list: function(username, oldPassword, newPassword) {
                return $http.get(cloudspaceconfig.apibaseurl + '/locations/list').then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            }
        };
    });
