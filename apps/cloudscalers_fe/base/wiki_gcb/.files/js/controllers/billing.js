angular.module('cloudscalers.controllers')
    .controller('BillingController', ['$scope', '$modal', 'Account', '$timeout', function($scope, $modal, Account, $timeout) {
   

    $scope.credit = "Unavailable";
    $scope.creditToAdd = 10;
    $scope.refreshTimeoutReference = null;
    
    
    $scope.refreshCredit = function(){
        Account.getCreditBalance($scope.currentAccount).then(
            function(result){
                $scope.credit = result.credit;
            },
            function(reason){
                $scope.credit = "Unavailable";
            }
        );
        Account.getCreditHistory($scope.currentAccount).then(
            function(result){
                $scope.transactions = result;
            }
        );
        $scope.refreshTimeoutReference = $timeout(function(){$scope.refreshCredit();}, 2000)
    }

    $scope.$on('$destroy',function(){
            $timeout.cancel($scope.refreshTimeoutReference);
    });
    
    $scope.refreshCredit();
    
    
    var bitcoinPaymentController = function($scope, $modalInstance, CryptoPayments){
        $scope.ok = function(){
            $modalInstance.close('confirmed');
        }
        CryptoPayments.getPaymentInfo($scope.currentAccount.id,'BTC').then(function(result){
            $scope.spinnerShow = true;
            $scope.bitcoin = true;
            $scope.paymentinfo = result;
            
            $scope.totalBtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);
        
            $scope.paymenturl = 'bitcoin:' +  $scope.paymentinfo.address + '?amount=' + $scope.totalBtc;
        }, function(error) {
            $scope.spinnerShow = true;
            $scope.bitcoin = false;
            $scope.bitcoinError = true;
        }
        );
            
    }
    
    $scope.payWithBitcoin = function(){
        
        var modalInstance = $modal.open({
              templateUrl: 'bitcoinModal.html',
              controller: bitcoinPaymentController,
              scope: $scope,
              resolve: {
                }
            });
    }
    var litecoinPaymentController = function($scope, $modalInstance, CryptoPayments){
        $scope.ok = function(){
            $modalInstance.close('confirmed');
        }
        CryptoPayments.getPaymentInfo($scope.currentAccount.id,'LTC').then(function(result){
            $scope.spinnerShow = true;
            $scope.litecoin = true;
            $scope.paymentinfo = result;
            
            $scope.totalLtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);
            
            $scope.paymenturl = 'litecoin:' +  $scope.paymentinfo.address + '?amount=' + $scope.totalLtc;
        }, function(error) {
            $scope.spinnerShow = true;
            $scope.litecoin = false;
            $scope.litecoinError = true;
        });
        
    }

    $scope.payWithLitecoin = function(){
        
        var modalInstance = $modal.open({
              templateUrl: 'litecoinModal.html',
              controller: litecoinPaymentController,
              scope: $scope,
              resolve: {
                }
            });
    }






    }]);