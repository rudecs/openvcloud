angular.module('cloudscalers.controllers')
    .controller('SignUpController', ['$scope', 'User', 'LocationsService', 'LoadingDialog','$window', '$modal', function($scope, User, LocationsService, LoadingDialog, $window, $modal) {
        $scope.passwordConfirmation = '';

        $scope.isPasswordConfirmed = true;
        $scope.canSignUp = false;
        $scope.signUpError = '';
        $scope.signUpResult = '';

        var uri = new URI($window.location);
        var queryparams = URI.parseQuery(uri.query());
        $scope.promocode = queryparams.promocode;

        var acceptTerms = '';
        var acceptBelgian = '';

        $scope.locations = {};
        LocationsService.list().then(function(locations) {
            $scope.locations = locations;
        });

        $scope.selectedLocation = 'ca1';
        $scope.$watch('locations',function(){
        	if (!($scope.selectedLocation in $scope.locations)){
            	$scope.selectedLocation = Object.keys($scope.locations)[0];
            }
        });
        
        
        $scope.changeLocation = function (locationcode) {
            $scope.selectedLocation = locationcode;
        };
        
        $scope.getLocationInfo = function(locationcode){
        	return LocationsService.get(locationcode);
        }

        $scope.$watch('user.username + user.password + email + passwordConfirmation + acceptTerms', function() {
                $scope.canSignUp =  $scope.user.username && $scope.email && $scope.acceptTerms
                	&& $scope.user.password && $scope.passwordConfirmation
        });
        $scope.signUp = function() {
            $scope.signUpResult = {};

            $scope.isPasswordConfirmed = $scope.user.password == $scope.passwordConfirmation  &&  $scope.user.password &&  $scope.passwordConfirmation;

            if ($scope.isPasswordConfirmed) {
                var isempty = function(val){
                    return (val === undefined || val == null || val.length <= 0) ? true : false;
                }
                if(isempty($scope.user.company)){
                    $scope.user.company = " ";
                }
                if(isempty($scope.user.companyurl)){
                    $scope.user.companyurl = " ";
                }
                $scope.signUpResult = User.signUp($scope.user.username, $scope.user.name, $scope.email, $scope.user.password ,$scope.user.company , $scope.user.companyurl
                    ,$scope.selectedLocation, $scope.promocode);
            }
        };

        $scope.$watch('signUpResult', function() {
            if ($scope.signUpResult) {
                $scope.signUpError = $scope.signUpResult.error;
                if ($scope.signUpResult.success) {
                    var uri = new URI($window.location);
                    uri.filename('SignUpValidation');
                    $window.location = uri.toString();
                }
            }
        }, true);


        var termsController = function ($scope, $modalInstance) {
            $scope.cancel = function () {
                $modalInstance.dismiss(acceptTerms);
            };
            if($scope.acceptTerms){
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
                 $('#accept-terms').removeAttr("disabled");
            scope.$apply();
        });
    };
});
