angular.module('cloudscalers.controllers')
    .controller('AccountController', ['$scope', function($scope) {
      
      $scope.$parent.$watch('currentAccount', function(){
      	$scope.preferredDataLocation = $scope.$parent.currentAccount.preferredDataLocation;
       });

    }]);