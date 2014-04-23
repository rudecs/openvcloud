angular.module('cloudscalers.controllers')
    .controller('PaypalPaymentController', ['$scope', '$modal', 'Account', '$timeout', '$ErrorResponseAlert', '$window', 'PaypalPayments',
      function($scope, $modal, Account, $timeout, $ErrorResponseAlert,$window, PaypalPayments) {

    $scope.payWithPayPal = function(){
    	PaypalPayments.initiatePayment($scope.currentAccount.id,$scope.creditToAdd, 'USD').then(
    				function(result){
    					$window.location = result.paypalurl;
    				},
    				function(reason){
    					$ErrorResponseAlert(reason);
    				}
    			);
    	
    }
    



    }]);
