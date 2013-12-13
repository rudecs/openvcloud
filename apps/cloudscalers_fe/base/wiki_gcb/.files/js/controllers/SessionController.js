angular.module('cloudscalers.controllers')
    .controller('SessionController', ['$scope', 'User', '$window', '$timeout', function($scope, User, $window, $timeout) {
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
        $timeout(function() {
            // Read the value set by browser autofill
            $scope.user.username = angular.element('[ng-model="user.username"]').val();
            $scope.user.password =angular.element('[ng-model="user.password"]').val();
        }, 0);
    }]);
