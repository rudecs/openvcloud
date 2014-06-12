angular.module('cloudscalers.controllers')
    .controller('TemplateManagementController', ['$scope', 'Account', 'Image','$modal','LoadingDialog','Machine','$timeout','$window', function($scope, Account, Image, $modal, LoadingDialog, Machine, $timeout, $window) {
      $scope.filteredTemplates = []
      $scope.templates =  Image.list($scope.currentAccount.id);
      $scope.$watch('templates',  function(){
              $scope.filteredTemplates = _.where($scope.templates, {"type": "Custom Templates"});
	     // console.log($scope.filteredTemplates);
            }, true);
      $scope.deleteTemplate = function(templateIndex) {
            var modalInstance = $modal.open({
                templateUrl: 'deleteTemplateDialog.html',
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
                LoadingDialog.show('Deleting Template');
                Machine.deleteTemplate(templateIndex)
                    .then(function() {
                        $timeout(function(){
                            $scope.filteredTemplates.splice( templateIndex , 1);
                            LoadingDialog.hide();
                        }, 1000);
                    }, function(reason) {
                        LoadingDialog.hide();
                        $ErrorResponseAlert(reason);
                    });
            });
        }
    }]);
