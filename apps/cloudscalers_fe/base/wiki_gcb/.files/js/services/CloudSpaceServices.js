
angular.module('cloudscalers.services')
	 .factory('CloudSpace',function ($http, $q, SessionData) {
    	return {
            list: function() {
            	 return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/list').then(
            			 function(result){
            				 return result.data;
            			 });

            },
            current: function() {
                return SessionData.getSpace();
            },
            setCurrent: function(space) {
                SessionData.setSpace(space);
            },
            create: function(name, accountId, userId) {
            	return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/create?name=' + encodeURIComponent(name)+'&accountId=' + accountId + '&access=['+ userId +']').then(
            			function(result){
            				return result.data;
            			},
            			function(reason){
            				$q.defer(reason);
            			}
            		);
            },
            get: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/get?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            $q.defer(reason);
                        }
                    );
            },
            addUser: function(space, user, accessType) {
                var accessString = '';
                for (var x in accessType) {
                    if (accessType[x])
                        accessString += x;
                }

                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/addUser?cloudspaceId=' + space.id +
                          '&accesstype=' + accessString + '&userId=' + user)
                    .then(function(reason) { 
                        return reason.data; 
                    }, function(result) { return result.data; });
            },
            deleteUser: function(space, userId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/deleteUser?cloudspaceId=' + space.id + 
                                 '&userId=' + userId)
                    .then(function(result) { return result.data; },
                          function(result) { return result.data; });
            }
        };
    });