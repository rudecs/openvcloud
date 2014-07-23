angular.module('cloudscalers.controllers')
    .controller('CloudSpaceManagementController', ['$scope', 'CloudSpace', 'LoadingDialog','$ErrorResponseAlert','$modal','$window', '$timeout','LocationsService', function($scope, CloudSpace, LoadingDialog, $ErrorResponseAlert, $modal, $window, $timeout, LocationsService) {

        $scope.cloudSpace = $scope.$parent.currentSpace.name;

	$scope.getLocationInfo = function(locationcode){
        	return LocationsService.get(locationcode);
        }

        $scope.deleteCloudspace = function() {
            var modalInstance = $modal.open({
                templateUrl: 'deleteCloudSpaceDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelDeletion = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });
            modalInstance.result.then(function (result) {
        		LoadingDialog.show('Deleting cloudspace');
                CloudSpace.delete($scope.currentSpace.id)
                    .then(function() {
                        $timeout(function(){
                            $scope.cloudspaces.splice(_.where($scope.cloudspaces, {id: $scope.currentSpace.id, accountId: $scope.currentSpace.accountId}), 1);
                            $scope.loadSpaces();
                            LoadingDialog.hide();
                            var uri = new URI($window.location);
                			uri.filename('Decks');
                            $window.location = uri.toString();
                        }, 1000);
                    }, function(reason) {
                        LoadingDialog.hide();
                        $ErrorResponseAlert(reason);
                    });
            });
        }
    }]);
