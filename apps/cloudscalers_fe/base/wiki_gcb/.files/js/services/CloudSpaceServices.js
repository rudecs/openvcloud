
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
            create: function(name, accountId, userId, location) {
            	return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/create?name=' + encodeURIComponent(name)+'&accountId=' + accountId + '&access=' + encodeURI(userId) + '&location=' + encodeURIComponent(location)).then(
            			function(result){
            				if (result.status == 200){
            					return result.data;
            				}
            				else {
            					return $q.reject(result);
            				}
            			},
            			function(reason){
            				return $q.reject(reason);
            			}
            		);
            },
            get: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/get?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            },
            getDefenseShield: function(cloudSpaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/getDefenseShield?cloudspaceId=' + cloudSpaceId).then(
                        function(result){
                            return result.data;
                        },
                        function(reason){
                            return $q.reject(reason);
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
                    .then(
                            function(result){ return result.data;},
                            function(reason) { return $q.reject(reason);});
            },
            deleteUser: function(space, userId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/deleteUser?cloudspaceId=' + space.id +
                                 '&userId=' + userId)
                    .then(function(result) { return result.data; },
                          function(reason) { return $q.reject(reason); });
            },
            delete: function(cloudspaceId) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/delete?cloudspaceId=' + cloudspaceId)
                    .then(function(result) { return result.data; },
                          function(reason) { return $q.reject(reason); });
            }
        };
    });
