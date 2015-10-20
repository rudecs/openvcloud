angular.module('cloudscalers.controllers')
    .controller('CloudSpaceManagementController', ['$scope', 'CloudSpace', 'LoadingDialog','$ErrorResponseAlert','$modal','$window', '$timeout','LocationsService', function($scope, CloudSpace, LoadingDialog, $ErrorResponseAlert, $modal, $window, $timeout, LocationsService) {

    $scope.getLocationInfo = function(locationcode){
            return LocationsService.get(locationcode);
        }

        $scope.$watch('currentSpace.id',function(){
            $scope.cloudSpaceSettingsLoader = true;
            CloudSpace.get($scope.currentSpace.id).then(
                    function(data) {
                        $scope.cloudSpaceDetails = data;
                        LocationsService.list().then(function(locations) {
                            $scope.currentLocation =  _.findWhere(locations, {locationCode: $scope.currentSpace.location});
                            $scope.cloudSpaceSettingsLoader = false;
                        });
                    },
                    function(reason) {
                        $ErrorResponseAlert(reason);
                        $scope.cloudSpaceSettingsLoader = false;
                    }
                    );
        });


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
                        $scope.cloudspaces.splice(_.where($scope.cloudspaces, {id: $scope.currentSpace.id, accountId: $scope.currentSpace.accountId}), 1);
                        $scope.setCurrentCloudspace($scope.cloudspaces[0]);
                        $scope.loadSpaces();
                        var ua = window.navigator.userAgent;
                        var msie = ua.indexOf("MSIE ");
                        if (msie > 0){
                            $window.location.reload();
                        }
                        else{
                            var uri = new URI($window.location);
                            uri.filename('Decks');
                            $window.location = uri.toString();
                        }
                    }, function(reason) {
                        LoadingDialog.hide();
                        $ErrorResponseAlert(reason);
                    });
            });
        }


    }]);
