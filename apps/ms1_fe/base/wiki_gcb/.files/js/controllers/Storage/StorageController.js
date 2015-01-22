angular.module('cloudscalers.controllers')
    .controller('StorageController', ['$scope', 'StorageService','$ErrorResponseAlert', '$alert', '$modal',
        function ($scope, StorageService, $ErrorResponseAlert, $alert, $modal) {
    		StorageService.listS3Buckets($scope.currentSpace.id).then(function(result) {
                    $scope.storages = result;
                }, function(reason){
			$ErrorResponseAlert(reason);
		});
	

 	var showCredentialsController= function($scope, $modalInstance, connectioninfo){
        	$scope.close = function(){
            		$modalInstance.close('close');
        	};
		$scope.s3server = connectioninfo.serverurl;
		$scope.accesskey = connectioninfo.accesskey;
		$scope.secretkey = connectioninfo.secretkey;
        }

    	$scope.showKeys = function(){
		StorageService.getS3info($scope.currentSpace.id).then(function(result) {

        		var modalInstance = $modal.open({
              			templateUrl: 'showCredentialsModal.html',
              			controller: showCredentialsController,
              			resolve: {connectioninfo: function(){return {serverurl:result.s3url,accesskey:result.accesskey,secretkey:result.secretkey};}}
            		});


		}, function(reason) {
			if (reason.status == 404){
				$alert("No S3 credentials found");
			} else {
				$ErrorResponseAlert(reason);
			}
		});
        }

        }
    ]);
