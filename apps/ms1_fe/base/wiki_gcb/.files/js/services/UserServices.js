
angular.module('cloudscalers.services')

	.factory('Users', function ($http, $q, SessionData) {
    	return {
            updatePassword: function(username, oldPassword, newPassword) {
                return $http.get(cloudspaceconfig.apibaseurl + '/users/updatePassword?username=' + encodeURIComponent(username) + '&oldPassword=' + encodeURIComponent(oldPassword) +
                    '&newPassword=' + encodeURIComponent(newPassword)
                    ).then(
                        function(result){
                            return result;
                        },
                        function(reason){
                            return $q.reject(reason);
                        }
                    );
            },
            sendResetPasswordLink: function(emailaddress){
            	return $http.get(cloudspaceconfig.apibaseurl + '/users/sendResetPasswordLink?emailaddress=' + encodeURIComponent(emailaddress) )
            	.then(
            			function(result){
            				return result;
            			},
            			function(reason){
            				return $q.reject(reason);
            			}
            		);
            },
            getResetPasswordInformation: function(resettoken){
            	return $http.get(cloudspaceconfig.apibaseurl + '/users/getResetPasswordInformation?resettoken=' + encodeURIComponent(resettoken))
            	.then(
            			function(result){
            				return result.data;
            			},
            			function(reason){
            				return $q.reject(reason);
            			}
            	);
            },
            resetPassword: function(resettoken, newpassword){
            	return $http.get(cloudspaceconfig.apibaseurl + '/users/resetPassword?resettoken=' + encodeURIComponent(resettoken) + '&newpassword=' + encodeURIComponent(newpassword))
            	.then(
            			function(result){
                                return result.data;
                        },
                        function(reason){
                                return $q.reject(reason);
                        }
                 );
            },
            activateUser: function(token, newpassword){
                return $http.get(cloudspaceconfig.apibaseurl + '/users/validate?validationtoken=' + encodeURIComponent(token) + '&password=' + encodeURIComponent(newpassword))
                .then(
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
