angular.module('cloudscalers.controllers')
    .controller('UsageController', ['$scope', 'Account', '$ErrorResponseAlert', '$window',
    function($scope, Account, $ErrorResponseAlert, $window) {

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


  }]);
