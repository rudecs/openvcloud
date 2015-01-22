angular.module('cloudscalers.controllers')
    .controller('UsageController', ['$scope', 'Account', '$ErrorResponseAlert', '$window',
    function($scope, Account, $ErrorResponseAlert, $window) {
      $scope.orderByField = 'name';
      $scope.reverseSort = false;
      $scope.$watch('currentAccount.id', function(){
        if ($scope.currentAccount && $scope.currentAccount.id) {
          var uri = new URI($window.location);
          var reference = uri.search(true).reference;

          Account.getUsage($scope.currentAccount, reference).
            then(function(result){
                    $scope.usagereport = result;
                  },
                  function(reason){
                    $ErrorResponseAlert(reason);
                  }
                );
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
