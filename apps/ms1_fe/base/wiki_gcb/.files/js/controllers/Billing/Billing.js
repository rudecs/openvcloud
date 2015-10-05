angular.module('cloudscalers.controllers')
    .controller('BillingController', ['$scope', '$modal', 'Account', '$timeout', '$ErrorResponseAlert', '$window',
      function($scope, $modal, Account, $timeout, $ErrorResponseAlert,$window) {


    $scope.credit = "Unavailable";
    $scope.creditToAdd = 10;

    $scope.refreshCredit = function(){
        Account.getCreditBalance($scope.currentAccount).then(
            function(result){
                $scope.credit = result.credit;
            },
            function(reason){
                $scope.credit = "Unavailable";
            }
        );

    }

    $scope.$watch('currentAccount', function () {
      if($scope.currentAccount){
        Account.getCreditHistory($scope.currentAccount).then(
            function(result){
                $scope.transactions = result;
            },
            function(reason) {
                $ErrorResponseAlert(reason);
            }
        );
      }
    });

    $scope.refreshCredit();


    var bitcoinPaymentController = function($scope, $modalInstance, CryptoPayments, $ErrorResponseAlert){
        $scope.ok = function(){
            $modalInstance.close('confirmed');
        }
        CryptoPayments.getPaymentInfo($scope.currentAccount.id,'BTC').then(function(result){
            $scope.spinnerShow = true;
            $scope.bitcoin = true;
            $scope.paymentinfo = result;

            $scope.totalBtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);

            $scope.paymenturl = 'bitcoin:' +  $scope.paymentinfo.address + '?amount=' + $scope.totalBtc;
        }, function(reason) {
            $scope.spinnerShow = true;
            $scope.bitcoin = false;
            // $scope.bitcoinError = true;
            $ErrorResponseAlert(reason);
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
    var litecoinPaymentController = function($scope, $modalInstance, CryptoPayments, $ErrorResponseAlert){
        $scope.ok = function(){
            $modalInstance.close('confirmed');
        }
        CryptoPayments.getPaymentInfo($scope.currentAccount.id,'LTC').then(function(result){
            $scope.spinnerShow = true;
            $scope.litecoin = true;
            $scope.paymentinfo = result;

            $scope.totalLtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);

            $scope.paymenturl = 'litecoin:' +  $scope.paymentinfo.address + '?amount=' + $scope.totalLtc;
        }, function(reason) {
            $scope.spinnerShow = true;
            $scope.litecoin = false;
            $ErrorResponseAlert(reason);
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

    $scope.showUsageDetails = function(reference){
        var uri = new URI($window.location);
        uri.filename('UsageReport');
        uri.addQuery('reference',reference)
        $window.location = uri.toString();
    }






    }]);
