cloudscalersControllers
    .controller('LoginController', ['$scope', 'User', 'APIKey', function($scope, User, APIKey) {
        $scope.username = '';
        $scope.password = '';
        $scope.loggedIn = !!APIKey.get();

        $scope.login = function() {            
            $scope.loginResult = User.login($scope.username, $scope.password);
        };

        $scope.logout = function() {
            User.logout();
            $scope.loggedIn = false;
        }

        $scope.$on('event:login-successful', function(loginResult) {
            location.href = '/test_gcb/buckets#/list';
        });
    }]);