angular.module('cloudscalers.controllers')
    .controller('SignUpController', ['$scope', 'User', 'LoadingDialog','$window', '$modal', function($scope, User, LoadingDialog, $window, $modal) {
        $scope.passwordConfirmation = '';

        $scope.isPasswordConfirmed = true;
        $scope.canSignUp = false;
        $scope.signUpError = '';
        $scope.signUpResult = '';
        $scope.user.password = " ";
        $scope.passwordConfirmation = " ";
        var acceptTerms = '';
        var acceptBelgian = '';
        $scope.$watch('user.username + user.password + email + passwordConfirmation + acceptTerms', function() {
                $scope.canSignUp =  $scope.user.username && $scope.email && $scope.acceptTerms;
             // && $scope.user.password && $scope.passwordConfirmation
        });
        $scope.signUp = function() {
            $scope.signUpResult = {};

            $scope.isPasswordConfirmed = $scope.user.password == $scope.passwordConfirmation;
            // && 
                // $scope.user.password && 
                // $scope.passwordConfirmation;

            if ($scope.isPasswordConfirmed) {
                $scope.signUpResult = User.signUp($scope.user.username, $scope.email, "stub" ,$scope.user.company , $scope.user.vat);
                // , $scope.user.password
            }
        };

        $scope.$watch('signUpResult', function() {
            if ($scope.signUpResult) {
                $scope.signUpError = $scope.signUpResult.error;
                if ($scope.signUpResult.success) {
                    // LoadingDialog.show('Creating account', 1000).then(function() {
                        $scope.waitlogin();
                    // });
                    // var uri = new URI($window.location);
                    // uri.filename('SignUpValidation');
                    // $window.location = uri.toString();
                }
            }
        }, true);


        var termsController = function ($scope, $modalInstance) {
            $scope.cancel = function () {
                $modalInstance.dismiss(acceptTerms);
            };
            if($scope.acceptTerms){
                $('#accept-terms').removeAttr("disabled");
                $('#accept-terms').prop('checked' , true);
            }
        };
            
        acceptTermsChanged = function(checkboxElem) {
          if (checkboxElem.checked) {
            $scope.acceptTerms = "accept";
          } else {
            $scope.acceptTerms = "";
          }
        }
                
        $scope.openTerms = function () {
            var modalInstance = $modal.open({
                templateUrl: 'termsDialog.html',
                controller: termsController,
                resolve: {},
                scope: $scope
            });
        };


    }]).directive("scroll", function ($window) {
    return function(scope, element, attrs) {
        angular.element($('#terms')).bind("scroll", function() {
            var scrollHeight = this.scrollHeight - this.scrollHeight / 2.5;
                if (this.scrollTop >= scrollHeight) {
                 $('#accept-terms').removeAttr("disabled");
             }
            scope.$apply();
        });
    };
});
