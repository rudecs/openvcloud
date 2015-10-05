angular.module('cloudscalers.controllers')
    .controller('UsageController', ['$scope', 'Account', '$ErrorResponseAlert', '$window', '$location',
    function($scope, Account, $ErrorResponseAlert, $window, $location) {
      $scope.orderByField = 'name';
      $scope.reverseSort = false;

        var uri = new URI($window.location);
        var reference = uri.search(true).reference;
        Account.getUsage($scope.currentAccount, reference).
          then(function(result){
                  $scope.usagereport = result;
                },
                function(reason){
                  // in case he don't have access to the page redirect to home
                  var uri = new URI($window.location);
                  uri.filename('Decks');
                  $window.location = uri.toString();
        });
        $scope.storeCurrentAccountId = $scope.currentAccount.id;

        $scope.$watch('currentAccount.id', function(){
          if ($scope.currentAccount.id) {
              if($scope.storeCurrentAccountId && $scope.storeCurrentAccountId != $scope.currentAccount.id){
                var uri = new URI($window.location);
                uri.filename('AccountSettings');
                uri.removeQuery('reference');
                $window.location = uri.toString();
              }
            }
        });
        var toUTCDate = function(date){
          var _utc = new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(),  date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds());
          return _utc;
        };

        var millisToUTCDate = function(millis){
          return toUTCDate(new Date(millis));
        };

          $scope.toUTCDate = toUTCDate;
          $scope.millisToUTCDate = millisToUTCDate;
  }]);
