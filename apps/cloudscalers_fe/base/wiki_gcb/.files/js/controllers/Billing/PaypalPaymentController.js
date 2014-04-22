angular.module('cloudscalers.controllers')
    .controller('PaypalPaymentController', ['$scope', '$modal', 'Account', '$timeout', '$ErrorResponseAlert', '$window', 'PaypalPayments',
      function($scope, $modal, Account, $timeout, $ErrorResponseAlert,$window, PaypalPayments) {

    $scope.payWithBitcoin = function(){
    	PaypalPayments.initiatePayment($scope.currentAccount.id,creditToAdd, 'USD').then(
    				function(result){
    					$window.location = result.paypalurl;
    				},
    				function(reason){
    					$ErrorResponseAlert(reason);
    				}
    			);
    	
    }
    



    }]);
