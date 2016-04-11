(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('BillingController', BillingController);

  function BillingController($scope, $modal, Account, $timeout, $ErrorResponseAlert, $window) {
    $scope.credit = 'Unavailable';
    $scope.creditToAdd = 10;
    $scope.refreshCredit = refreshCredit;
    $scope.payWithBitcoin = payWithBitcoin;
    $scope.payWithLitecoin = payWithLitecoin;
    $scope.showUsageDetails = showUsageDetails;

    // Binding and Watch
    $scope.$watch('currentAccount', currentAccount);

    // Initialization: Functions invokation logic
    $scope.refreshCredit();

    // Functions
    function refreshCredit() {
      Account.getCreditBalance($scope.currentAccount).then(
        function(result) {
          $scope.credit = result.credit;
        },
        function() {
          $scope.credit = 'Unavailable';
        }
      );
    }

    function currentAccount() {
      $scope.transactionsLoader = true;
      $scope.transactions = {};
      if ($scope.currentAccount) {
        Account.getCreditHistory($scope.currentAccount).then(
          function(result) {
            $scope.transactions = result;
            $scope.transactionsLoader = false;
          },
          function(reason) {
            $ErrorResponseAlert(reason);
            $scope.transactionsLoader = false;
          }
        );
      }
    }

    function bitcoinPaymentController($scope, $modalInstance, CryptoPayments, $ErrorResponseAlert) {
      $scope.ok = function() {
        $modalInstance.close('confirmed');
      };
      CryptoPayments.getPaymentInfo($scope.currentAccount.id,'BTC')
      .then(
        function(result) {
          $scope.spinnerShow = true;
          $scope.bitcoin = true;
          $scope.paymentinfo = result;
          $scope.totalBtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);

          $scope.paymenturl = 'bitcoin:' + $scope.paymentinfo.address + '?amount=' + $scope.totalBtc;
        }, function(reason) {
          $scope.spinnerShow = true;
          $scope.bitcoin = false;
          // $scope.bitcoinError = true;
          $ErrorResponseAlert(reason);
        }
      );
    }

    function payWithBitcoin() {
      $modal.open({
        templateUrl: 'bitcoinModal.html',
        controller: bitcoinPaymentController,
        scope: $scope,
        resolve: {}
      });
    }

    function litecoinPaymentController($scope, $modalInstance, CryptoPayments, $ErrorResponseAlert) {
      $scope.ok = function() {
        $modalInstance.close('confirmed');
      };
      CryptoPayments.getPaymentInfo($scope.currentAccount.id,'LTC').then(function(result) {
        $scope.spinnerShow = true;
        $scope.litecoin = true;
        $scope.paymentinfo = result;

        $scope.totalLtc = ($scope.creditToAdd / $scope.paymentinfo.value).toFixed(8);

        $scope.paymenturl = 'litecoin:' + $scope.paymentinfo.address + '?amount=' + $scope.totalLtc;
      }, function(reason) {
        $scope.spinnerShow = true;
        $scope.litecoin = false;
        $ErrorResponseAlert(reason);
      });
    }

    function payWithLitecoin() {
      $modal.open({
        templateUrl: 'litecoinModal.html',
        controller: litecoinPaymentController,
        scope: $scope,
        resolve: {}
      });
    }

    function showUsageDetails(reference) {
      var uri = new URI($window.location);
      uri.filename('UsageReport');
      uri.addQuery('reference',reference);
      $window.location = uri.toString();
    }
  }
})();
