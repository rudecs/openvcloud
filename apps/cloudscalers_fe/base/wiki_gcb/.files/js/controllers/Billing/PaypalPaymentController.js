angular.module('cloudscalers.controllers')
    .controller('PaypalPaymentController', ['$scope', '$modal', 'Account', '$timeout', '$ErrorResponseAlert', '$window', 'PaypalPayments', '$alert',
      function($scope, $modal, Account, $timeout, $ErrorResponseAlert,$window, PaypalPayments, $alert) {

    $scope.payWithPayPal = function(){
        if($scope.creditToAdd >= 10){
            PaypalPayments.initiatePayment($scope.currentAccount.id,$scope.creditToAdd, 'USD').then(
                        function(result){
                            $window.location = result.paypalurl;
                        },
                        function(reason){
                            $ErrorResponseAlert(reason);
                        }
                    );
        }
        else{
            $alert("A minimum of 10 USD is required");
        }
        
    }
    



    }]);
