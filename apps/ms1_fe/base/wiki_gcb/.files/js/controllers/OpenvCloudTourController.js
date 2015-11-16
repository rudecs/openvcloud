angular.module('cloudscalers.controllers')
    .controller('OpenvCloudTourController', ['$scope', 'ipCookie', 'Users', '$ErrorResponseAlert', function($scope, ipCookie, Users, $ErrorResponseAlert) {
        $scope.steps = {};
        $scope.tourtips = true;
        $scope.steps['tourStep'] = ipCookie('tourStep') || 0;
        $scope.steps['portForwardTourStep'] = ipCookie('portForwardTourStep') || 0;
        $scope.steps['machineDetailTourStep'] = ipCookie('machineDetailTourStep') || 0;
        $scope.steps['machineListTourStep'] = ipCookie('machineListTourStep') || 0;

        // Saving tour progress in cookies
        $scope.postStepCallback = function() {
            ipCookie('tourStep', $scope.steps['tourStep']);
            ipCookie('portForwardTourStep', $scope.steps['portForwardTourStep']);
            ipCookie('machineDetailTourStep', $scope.steps['machineDetailTourStep']);
            ipCookie('machineListTourStep', $scope.steps['machineListTourStep']);
        };

        $scope.tourComplete = function(tourName) {
            ipCookie(tourName, 9999);
        };

        $scope.DisableTourForEverModal = function() {
            $scope.tourComplete("tourStep");
            $scope.tourComplete("portForwardTourStep");
            $scope.tourComplete("machineDetailTourStep");
            $scope.tourComplete("machineListTourStep");
            $scope.cancelDisableTourForEverModal();
            $scope.tourtips = false;
            Users.disableTourTips().then(function() {

            },function(reason){
                $ErrorResponseAlert(reason);
            });
        };

        $scope.disableTourForEverModal = function() {
            angular.element("#disableTourDialog").modal("show");
        };

        $scope.cancelDisableTourForEverModal = function() {
            angular.element("#disableTourDialog").modal("hide");
        };

    }]);
