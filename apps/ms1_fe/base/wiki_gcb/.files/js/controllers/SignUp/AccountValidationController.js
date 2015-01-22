angular.module('cloudscalers.controllers')
    .controller('AccountValidationController', ['$scope','$window','$ErrorResponseAlert', 'PaypalPayments', function($scope, $window, $ErrorResponseAlert, PaypalPayments) {


        $scope.validateWithPayPal = function(){
                PaypalPayments.initiateAccountValidation().then(
                            function(result){
                                $window.location = result.paypalurl;
                            },
                            function(reason){
                                $ErrorResponseAlert(reason);
                            }
                        );
        }
    }]);
