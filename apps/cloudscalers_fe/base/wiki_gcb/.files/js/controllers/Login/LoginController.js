cloudscalersControllers
    .controller('LoginController', ['$scope', 'User', 'APIKey','$window', function($scope, User, APIKey, $window) {
        $scope.username = '';
        $scope.password = '';
        $scope.loggedIn = !!APIKey.get();

        $scope.login = function() {            
            $scope.loginResult = User.login($scope.username, $scope.password);
        };

        $scope.logout = function() {
            User.logout();
            $scope.loggedIn = false;
            
			var uri = new URI($window.location);
			uri.filename('');
			$window.location = uri.toString();
        }

        $scope.$on('event:login-successful', function(loginResult) {
        	var uri = new URI($window.location);
			uri.filename('buckets#/list');
			$window.location = uri.toString();
        });
    }]);
