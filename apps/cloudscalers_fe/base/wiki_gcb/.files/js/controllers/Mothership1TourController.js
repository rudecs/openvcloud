angular.module('cloudscalers.controllers')
    .controller('Mothership1TourController', ['$scope', 'ipCookie', function($scope, ipCookie) {
        $scope.tourStep = ipCookie('tourStep') || 0; 
        $scope.portForwardTourStep = ipCookie('portForwardTourStep') || 0;
        $scope.machineDetailTourStep = ipCookie('machineDetailTourStep') || 0;
        $scope.machineListTourStep = ipCookie('machineListTourStep') || 0;
        
        // Saving tour progress in cookies
        $scope.postStepCallback = function() {
            ipCookie('tourStep', $scope.tourStep);
            ipCookie('portForwardTourStep', $scope.portForwardTourStep);
            ipCookie('machineDetailTourStep', $scope.machineDetailTourStep);
            ipCookie('machineListTourStep', $scope.machineListTourStep);
        };
        
    }]);
