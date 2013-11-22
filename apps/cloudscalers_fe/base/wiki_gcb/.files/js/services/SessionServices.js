


angular.module('cloudscalers.SessionServices', ['ng'])

	.factory('authenticationInterceptor',['$q','$log', 'SessionData', function($q, $log, SessionData){
        return {
            'request': function(config) {
                if (config) {
                    url = config.url;

                    if(/\/machines\//i.test(url) || /\/sizes\//i.test(url) || /\/images\//i.test(url)) {
                        uri = new URI(url);
                        uri.addSearch('api_key', SessionData.get());
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
    .factory('SessionData', function($window) {
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
    .factory('User', function ($http, SessionData, $q) {
        var user = {};
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
            			SessionData.set(result.data);
            			return result.data;
            		},
            		function (reason) {
            			SessionData.set(undefined);
                        return $q.reject(reason); }
            );
        };

        user.logout = function() {
        	SessionData.clear();
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
        }
        
        return user;
        
    });
