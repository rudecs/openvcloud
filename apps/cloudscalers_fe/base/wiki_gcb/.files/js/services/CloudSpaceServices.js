
angular.module('cloudscalers.services')

	 .factory('CloudSpace',function ($http, $q, SessionData) {
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

            },
            current: function() {
                return SessionData.getSpace();
            },
            setCurrent: function(space) {
                SessionData.setSpace(space);
            },
            create: function(name, accountId) {
            	return $http.get(cloudspaceconfig.apibaseurl + '/cloudspace/create').then(
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