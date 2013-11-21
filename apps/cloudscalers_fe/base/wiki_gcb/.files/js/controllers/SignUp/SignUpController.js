angular.module('cloudscalers.controllers')
    .controller('SignUpController', ['$scope', 'User', function($scope, User) {
        $scope.username = '';
        $scope.password = '';
        $scope.passwordConfirmation = '';

        $scope.isPasswordConfirmed = true;
        $scope.canSignUp = false;
        $scope.signUpError = '';
        $scope.signUpResult = '';

        $scope.$watch('username + password + passwordConfirmation', function() {
            $scope.canSignUp = !!($scope.username && $scope.password && $scope.passwordConfirmation);
        });

        $scope.signUp = function() {
            $scope.signUpResult = {};

            $scope.isPasswordConfirmed = $scope.password == $scope.passwordConfirmation && 
                $scope.password && 
                $scope.passwordConfirmation;

            if ($scope.isPasswordConfirmed)
                $scope.signUpResult = User.signUp($scope.username, $scope.password);
        };

        $scope.$watch('signUpResult', function() {
            if ($scope.signUpResult) {
                $scope.signUpSuccess = $scope.signUpResult.success;
                $scope.signUpError = $scope.signUpResult.error;
            }
        }, true);
    }]);