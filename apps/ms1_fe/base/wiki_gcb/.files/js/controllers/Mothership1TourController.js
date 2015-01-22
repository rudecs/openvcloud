angular.module('cloudscalers.controllers')
    .controller('Mothership1TourController', ['$scope', 'ipCookie', function($scope, ipCookie) {
        $scope.steps = {};
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
        
    }]);
