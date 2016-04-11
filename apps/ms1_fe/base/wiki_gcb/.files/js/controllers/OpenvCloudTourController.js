(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('OpenvCloudTourController', OpenvCloudTourController);
  function OpenvCloudTourController($scope, ipCookie, Users, SessionData, User, $ErrorResponseAlert) {
    $scope.steps = {};
    $scope.tourtips = true;
    $scope.steps['tourStep'] = ipCookie('tourStep') || 0;
    $scope.steps['portForwardTourStep'] = ipCookie('portForwardTourStep') || 0;
    $scope.steps['machineDetailTourStep'] = ipCookie('machineDetailTourStep') || 0;
    $scope.steps['machineListTourStep'] = ipCookie('machineListTourStep') || 0;
    // Saving tour progress in cookies
    $scope.postStepCallback = postStepCallback;
    $scope.tourComplete = tourComplete;
    $scope.tourReset = tourReset;
    $scope.DisableTourForEverModal = DisableTourForEverModal;
    $scope.disableTourForEverModal = disableTourForEverModal;
    $scope.cancelDisableTourForEverModal = cancelDisableTourForEverModal;

    // Binding and Watch
    $scope.$watch('currentUser', currentUser);

    // Functions
    function postStepCallback() {
      ipCookie('tourStep', $scope.steps['tourStep']);
      ipCookie('portForwardTourStep', $scope.steps['portForwardTourStep']);
      ipCookie('machineDetailTourStep', $scope.steps['machineDetailTourStep']);
      ipCookie('machineListTourStep', $scope.steps['machineListTourStep']);
    }

    function tourComplete(tourName) {
      ipCookie(tourName, 9999);
    }

    function tourReset(tourName) {
      ipCookie(tourName, 0);
    }

    function currentUser() {
      if ($scope.currentUser) {
        User.updateUserDetails($scope.currentUser.username).then(
          function(currentUserData) {
            if (currentUserData.tourTips === undefined) {
              if (ipCookie('tourStep') === 9999) {
                currentUserData['tourTips'] = true;
              }else {
                currentUserData['tourTips'] = false;
              }
              Users.tourTipsSwitch(currentUserData['tourTips']).then(function() {
                SessionData.setUser(currentUserData);
              },function(reason) {
                $ErrorResponseAlert(reason);
              });
              return;
            }
            $scope.currentUserDisableTourTips = JSON.parse(currentUserData.tourTips);
            if ($scope.currentUserDisableTourTips === false) {
              $scope.tourComplete('tourStep');
              $scope.tourComplete('portForwardTourStep');
              $scope.tourComplete('machineDetailTourStep');
              $scope.tourComplete('machineListTourStep');
              $scope.tourtips = false;
            }else if ($scope.currentUserDisableTourTips === true) {
              $scope.tourReset('tourStep');
              $scope.tourReset('portForwardTourStep');
              $scope.tourReset('machineDetailTourStep');
              $scope.tourReset('machineListTourStep');
              $scope.tourtips = true;
            }
          },
          function(reason) {
            $ErrorResponseAlert(reason);
          }
        );
      }
    }

    function DisableTourForEverModal() {
      $scope.tourComplete('tourStep');
      $scope.tourComplete('portForwardTourStep');
      $scope.tourComplete('machineDetailTourStep');
      $scope.tourComplete('machineListTourStep');
      $scope.cancelDisableTourForEverModal();
      $scope.tourtips = false;
      Users.tourTipsSwitch(false).then(function() {
        var currentUserData = SessionData.getUser();
        currentUserData['tourTips'] = false;
        SessionData.setUser(currentUserData);
      },function(reason) {
        $ErrorResponseAlert(reason);
      });
    }

    function disableTourForEverModal() {
      angular.element('#disableTourDialog').modal('show');
    }

    function cancelDisableTourForEverModal() {
      angular.element('#disableTourDialog').modal('hide');
    }
  }
})();
