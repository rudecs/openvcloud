(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('sideNavController', sideNavController);

  function sideNavController($scope, $rootScope) {
    $scope.machinDeckCall = function() {
      $rootScope.$emit('callUpdateMachineList', {});
    };
  }
})();
