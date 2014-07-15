
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
            },
            getCountryForLocation: function(location){
            	var countries = {'ca1': 'Canada', 'us1': 'United States', 'uk1': 'United Kingdom', 'be': 'Belgium'};
            	return countries[location];
            }
        };
    });
