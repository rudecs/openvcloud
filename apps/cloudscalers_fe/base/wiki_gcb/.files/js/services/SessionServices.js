


angular.module('cloudscalers.SessionServices', ['ng'])

	.factory('authenticationInterceptor',['$q','$log', 'APIKey', function($q, $log, APIKey){
        return {
            'request': function(config) {
                if (config) {
                    url = config.url;

                    if(/\/machines\//i.test(url) || /\/sizes\//i.test(url) || /\/images\//i.test(url)) {
                        uri = new URI(url);
                        uri.addSearch('api_key', APIKey.get());
                        config.url = uri.toString();
    				}
                }
                return config || $q.when(config);
    	    },
    	    'response': function(response) {
                $log.log("Response intercepted");
                return response || $q.when(response);
            }
        };
	}])
    .factory('APIKey', function($window) {
        var clientApiKey;
        return {
            get: function() { 
                return $window.sessionStorage.getItem('gcb:api_key');
            },
            set: function(apiKey) {
                $window.sessionStorage.setItem('gcb:api_key', apiKey);
            },
            clear: function() {
                $window.sessionStorage.removeItem('gcb:api_key');
            }
        };
    })
    .factory('User', function ($http, $q, $window, APIKey) {
        var user = {};
        
        user.current = function() {
            // If method is called with no parameters, then retrieve the current user & return it
            if (arguments.length == 0)
                return JSON.parse($window.localStorage.getItem('gcb:currentUser'));

            // If method is called with `null` or `undefined`, clear the current user
            if (arguments.length == 1 && !arguments[0])
                $window.localStorage.clear('gcb:currentUser');

            $window.localStorage.setItem('gcb:currentUser', JSON.stringify(arguments[0]));
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
            			APIKey.set(result.data);
                        user.current({'username': username});
            			return result.data;
            		},
            		function (reason) {
                        APIKey.clear();
                        user.current(undefined);
                        return $q.reject(reason); 
                    }
            );
        };

        user.logout = function() {
            APIKey.clear();
            user.current(undefined);
        };

        user.signUp = function(username, email, password) {
            var signUpResult = {};
            $http({
                method: 'POST',
                data: {
                    username: username,
                    email: email,
                    password: password
                },
                url: cloudspaceconfig.apibaseurl + '/users/signup'
            })
            .success(function(data, status, headers, config) {
                signUpResult.success = true;
            })
            .error(function(data, status, headers, config) {
                signUpResult.error = data;
            });
            return signUpResult;
        };
        
        return user;
        
    });
