angular.module('cloudscalers.controllers')
    .controller('CloudSpaceManagementController', ['$scope', 'CloudSpace', 'LoadingDialog','$alert','$modal','$window', function($scope, CloudSpace, LoadingDialog, $alert, $modal, $window) {

        $scope.deleteCloudspace = function(space) {
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
                CloudSpace.delete(space)
                    .then(function() {
                        $scope.loadSpaces();
                        LoadingDialog.hide();
                        var uri = new URI($window.location);
            			uri.filename('MachineBuckets');
            			$window.location = uri.toString();
                    }, function(data) {
                        LoadingDialog.hide();
                        $alert(data);
                    });
            });
        }
    }]);