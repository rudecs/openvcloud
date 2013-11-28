
angular.module('cloudscalers.CloudSpaceServices', ['ng','cloudscalers.SessionServices'])

	.config(['$httpProvider',function($httpProvider) {
        $httpProvider.interceptors.push('authenticationInterceptor');
	}])
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
            addUser: function(space, user, accessType) {
                var accessString = '';
                for (var x in accessType) {
                    if (accessType[x])
                        accessString += x;
                }

                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/addUser?cloudSpaceId=' + space.cloudSpaceId +
                          '&accesstype=' + accessString + '&userId=' + user.id)
                    .then(function(reason) { return reason.data; },
                          function(reason) { return reason.data; });
            },
            deleteUser: function(space, user) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/deleteUser?cloudSpaceId=' + space.cloudSpaceId + 
                                 '&userId=' + user.id)
                    .then(function(result) { return result.data; },
                          function(result) { return result.data; });
            },
            listUsers: function(space) {
                return $http.get(cloudspaceconfig.apibaseurl + '/cloudspaces/listUsers?cloudSpaceId=' + space.cloudSpaceId)
                    .then(function(reason) { return reason.data; },
                          function(reason) { return reason.data; });
            }
        };
    });