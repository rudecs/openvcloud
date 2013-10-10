cloudscalersControllers
    .controller('SignUpController', ['$scope', 'User', function($scope, User) {
        $scope.username = '';
        $scope.password = '';
        $scope.passwordConfirmation = '';

        $scope.isPasswordConfirmed = true;
        $scope.canSignUp = false;
        $scope.signUpError = '';

        $scope.$watch('username + password + passwordConfirmation', function() {
            $scope.canSignUp = !!($scope.username && $scope.password && $scope.passwordConfirmation);
        });

        $scope.validatePasswordConfirmation = function() {
            $scope.isPasswordConfirmed = $scope.password == $scope.passwordConfirmation && 
                $scope.password && 
                $scope.passwordConfirmation;
        };

        $scope.signUp = function() {
            User.signUp($scope.username, $scope.password);
        };

        $scope.$on('event:signUp-successful', function(loginResult) {
            $scope.signUpSuccess = true;
            $scope.signUpError = false;
        });

        $scope.$on('event:signUp-error', function(loginResult) {
            $scope.signUpError = 'Error in signup';
            $scope.signUpSuccess = false;
        });
    }]);