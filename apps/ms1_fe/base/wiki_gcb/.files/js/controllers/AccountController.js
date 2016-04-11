(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('AccountController', AccountController);

  function AccountController($scope) {
    $scope.$parent.$watch('currentAccount', function() {
      $scope.accountNames = $scope.$parent.currentAccount.name;
      $scope.preferredDataLocation = $scope.$parent.currentAccount.preferredDataLocation;
    });
  }
})();
