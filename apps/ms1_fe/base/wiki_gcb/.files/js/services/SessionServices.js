angular.module('cloudscalers.services')

	.factory('authenticationInterceptor',['$q', 'SessionData', '$window', function($q, SessionData, $window){
        return {
            'request': function(config) {
                if (config) {
                    var url = config.url;

                    if(! /((pages)|(template)\/)|(\.html)/i.test(url)){

                    	var currentUser = SessionData.getUser();
                    	if (currentUser){
                    		var uri = new URI(url);
                       		uri.addSearch('authkey', currentUser.api_key);
                       		config.url = uri.toString();
    					}
                    }
                }
                return config || $q.when(config);
    	    },
    	    'response': function(response) {
                return response || $q.when(response);
            },

           'responseError': function(rejection) {
        	   if (rejection.status == 401 || rejection.status == 419){
        		   var uri = new URI($window.location);

       				uri.filename('Login');
       				uri.fragment('');
       				$window.location = uri.toString();
        	   }
               return $q.reject(rejection);
            }
        };
	}])
    .factory('SessionData', function($window) {
        return {
        	getUser : function(){
        			var userdata = $window.sessionStorage.getItem('gcb:currentUser');
        			if (userdata){
        				return JSON.parse(userdata);
        			}
        		},
        	setUser : function(userdata){
        			if (userdata){
        				$window.sessionStorage.setItem('gcb:currentUser', JSON.stringify(userdata));
        			}
        			else{
        				$window.sessionStorage.removeItem('gcb:currentUser');
        			}
        		},
            getSpace : function() {
                var space = $window.sessionStorage.getItem('gcb:currentSpace');
                if (!space) {
                    space = $window.localStorage.getItem('gcb:currentSpace');
                }

                if (space) {
                    return JSON.parse(space);
                }
            },
            setSpace : function(space){
                    if (space){
                        $window.sessionStorage.setItem('gcb:currentSpace', JSON.stringify(space));
                    }
                    else{
                        $window.sessionStorage.removeItem('gcb:currentSpace');
                    }
                },
            };
    })
    .factory('User', function ($http, SessionData, $q) {
        var user = {};

        user.current = function() {
            return SessionData.getUser();
        };

        user.login = function (username, password) {
            return $http({
                method: 'POST',
                data: {
                    username: username,
                    password: password
                },
                url: cloudspaceconfig.apibaseurl + '/users/authenticate'
            }).then(
            		function (result) {
            			SessionData.setUser({username: username, api_key: JSON.parse(result.data)});
            			return result;
            		},
            		function (reason) {
            			if (reason.status == 409){
            				SessionData.setUser({username: username, api_key: reason.data});
                			return reason;
            			}
            			else{
            				SessionData.setUser(undefined);
            				return $q.reject(reason); 
            			}
            		}
            );
        };

        user.get = function(username){
        	url = cloudspaceconfig.apibaseurl +'/users/get?username=' + encodeURIComponent(username)
        	var currentUser = SessionData.getUser();
        	if (currentUser){
        		var uri = new URI(url);
           		uri.addSearch('authkey', currentUser.api_key);
           		url = uri.toString();
			}
        	return $http.get(url);
        }

        user.updateUserDetails= function(username){
        	return user.get(username).then(
        			function(result){
        				storedUser = SessionData.getUser();
        				storedUser.emailaddresses = result.data.emailaddresses;
        				SessionData.setUser(storedUser);
        				return storedUser;
        			},
        			function(reason){
                        return $q.reject(reason);
                    }
        			);

        }

        user.logout = function() {
        	SessionData.setUser(undefined);
        };

        return user;

    });
