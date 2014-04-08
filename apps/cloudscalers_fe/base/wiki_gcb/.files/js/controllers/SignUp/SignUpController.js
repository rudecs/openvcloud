angular.module('cloudscalers.controllers')
    .controller('SignUpController', ['$scope', 'User', 'LoadingDialog','$window', function($scope, User, LoadingDialog, $window) {
        $scope.passwordConfirmation = '';

        $scope.isPasswordConfirmed = true;
        $scope.canSignUp = false;
        $scope.signUpError = '';
        $scope.signUpResult = '';
        $scope.$watch('user.username + user.password + email + passwordConfirmation', function() {
            $scope.canSignUp = $scope.user.username && $scope.email && $scope.user.password && $scope.passwordConfirmation;
        });
        $scope.signUp = function() {
            $scope.signUpResult = {};

            $scope.isPasswordConfirmed = $scope.user.password == $scope.passwordConfirmation && 
                $scope.user.password && 
                $scope.passwordConfirmation;

            if ($scope.isPasswordConfirmed) {
                $scope.signUpResult = User.signUp($scope.user.username, $scope.email, $scope.user.password);
            }
        };

        $scope.$watch('signUpResult', function() {
            if ($scope.signUpResult) {
                $scope.signUpError = $scope.signUpResult.error;
                if ($scope.signUpResult.success) {
                    LoadingDialog.show('Creating account', 100000000).then(function() {
                        $scope.login();
                    });
                }
            }
        }, true);
    }]);
