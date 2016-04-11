(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('UsageController', UsageController);

  function UsageController($scope, Account, $ErrorResponseAlert, $window) {
    var uri = new URI($window.location);
    var reference = uri.search(true).reference;
    $scope.orderByField = 'name';
    $scope.reverseSort = false;
    $scope.usagereportLoader = true;
    $scope.storeCurrentAccountId = $scope.currentAccount.id;
    $scope.toUTCDate = toUTCDate;
    $scope.millisToUTCDate = millisToUTCDate;

    $scope.$watch('currentAccount.id', currentAccountId);

    initAccountUsage();

    function initAccountUsage() {
      Account.getUsage($scope.currentAccount, reference)
      .then(function(result) {
        $scope.usagereport = result;
        $scope.usagereportLoader = false;
      }, function() {
        // in case he don't have access to the page redirect to home
        var uri = new URI($window.location);
        uri.filename('Decks');
        $window.location = uri.toString();
      });
    }

    function currentAccountId() {
      if ($scope.currentAccount.id) {
        if ($scope.storeCurrentAccountId && $scope.storeCurrentAccountId !== $scope.currentAccount.id) {
          var uri = new URI($window.location);
          uri.filename('AccountSettings');
          uri.removeQuery('reference');
          $window.location = uri.toString();
        }
      }
    }

    function toUTCDate(date) {
      var _utc = new Date(
        date.getUTCFullYear(),
        date.getUTCMonth(),
        date.getUTCDate(),
        date.getUTCHours(),
        date.getUTCMinutes(),
        date.getUTCSeconds());
      return _utc;
    }

    function millisToUTCDate(millis) {
      return toUTCDate(new Date(millis));
    }
  }

})();
