angular.module('cloudscalers.controllers')
    .controller('sideNavController', ['$scope', '$rootScope',
        function ($scope ,$rootScope) {
          $scope.machinDeckCall = function () {
            $rootScope.$emit('callUpdateMachineList', {});
          };
        }]);
