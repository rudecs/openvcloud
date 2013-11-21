angular.module('cloudscalers.controllers')
    .controller('SessionController', ['$scope', 'User', 'APIKey','$window', function($scope, User, APIKey, $window) {
        $scope.user = {username : '', password:''};
       
        $scope.login_error = undefined;
        
        $scope.login = function() {            
            User.login($scope.user.username, $scope.user.password).
            then(
            		function(result) {
            			$scope.login_error = undefined;
            			var uri = new URI($window.location);
            			uri.filename('MachineBuckets');
            			$window.location = uri.toString();
            		},
            		function(reason) {
            			$scope.login_error = reason.status;
            		}
            );
        };

        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			$window.location = uri.toString();
        }

    }]);
