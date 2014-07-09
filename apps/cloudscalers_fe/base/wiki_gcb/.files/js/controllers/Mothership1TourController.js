angular.module('cloudscalers.controllers')
    .controller('Mothership1TourController', ['$scope', 'ipCookie', function($scope, ipCookie) {
        $scope.tourStep = ipCookie('tourStep') || 0;

        // Saving tour progress in cookies
        $scope.postStepCallback = function() {
            ipCookie('tourStep', $scope.tourStep);
        };

    }]);