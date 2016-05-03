(function() {
  'use strict';
  //jshint latedef: nofunc
  angular.module('cloudscalers.controllers')
  .controller('NetworkController', NetworkController);

  function NetworkController($scope, Networks, Machine, $modal, $interval,
      $sce, CloudSpace, $ErrorResponseAlert, $timeout) {

    var cloudspaceupdater;
    $scope.showDefenseShield = showDefenseShield;
    $scope.downloadOpenvpnConfig = downloadOpenvpnConfig;
    $scope.$watch('currentSpace.id + currentSpace.status', currentSpaceIdAndStatus);
    $scope.$on('$destroy', destroy);

    function routerosController($scope, $modalInstance) {
        $timeout(function() {
          angular.element('.routeros-modal-header').parents('.modal').addClass('routeros-modal');
        }, 100);
        $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
        };
        var defenseshieldautologin = 'autologin=' + $scope.defenseshield.user + '|' + $scope.defenseshield.password;
        $scope.defenseshieldframe = $sce.trustAsHtml('<iframe name="' + defenseshieldautologin +
        '" src="' + $scope.defenseshield.url + '" style="width:100%;height:80%"></iframe>');
      }

    function showDefenseShield() {
        CloudSpace.getDefenseShield($scope.currentSpace.id)
        .then(
          function(shieldobj) {
            $scope.defenseshield = shieldobj;
            $modal.open({
              templateUrl: 'routerosDialog.html',
              controller: routerosController,
              resolve: {},
              scope: $scope
            });
          }, function(reason) {
            $ErrorResponseAlert(reason);
          }
        );
      }

    function downloadOpenvpnConfig() {
        CloudSpace.getOpenvpnConfig($scope.currentSpace.id);
    }

    function currentSpaceIdAndStatus() {
        if ($scope.currentSpace) {
          if ($scope.currentSpace.status !== 'DEPLOYED') {
            if (!(angular.isDefined(cloudspaceupdater))) {
              cloudspaceupdater = $interval($scope.loadSpaces,5000);
            }
          } else {
            if (angular.isDefined(cloudspaceupdater)) {
              $interval.cancel(cloudspaceupdater);
              cloudspaceupdater = undefined;
            }
          }
        }
      }

    function destroy() {
        if (angular.isDefined(cloudspaceupdater)) {
          $interval.cancel(cloudspaceupdater);
          cloudspaceupdater = undefined;
        }
      }
  }
})();
