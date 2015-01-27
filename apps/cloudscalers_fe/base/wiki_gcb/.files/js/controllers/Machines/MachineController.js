
angular.module('cloudscalers.controllers')
    .controller('MachineController', ['$scope', 'Machine', 'Size', 'Image', '$ErrorResponseAlert',
      function($scope, Machine, Size, Image, $ErrorResponseAlert) {


        $scope.$watch('currentspace.accountId',function(){
        	if ($scope.currentSpace){
        		$scope.images = Image.list($scope.currentSpace.accountId, $scope.currentSpace.id);
        	}
        });

        $scope.updateMachineList = function(){
        	if ($scope.currentSpace){
        		Machine.list($scope.currentSpace.id).then(
					function(machines){
				      $scope.machines = machines;
					},
					function(reason){
						$ErrorResponseAlert(reason);
					}
        		);
    		}
        }
        
    	$scope.$watch('currentSpace.id',function(){
    		$scope.updateMachineList();
    	});

    	$scope.machineIsManageable = function(machine){
    		return machine.status != 'DESTROYED';
    	}

        $scope.sizes = Size.list($scope.currentSpace.id);
        $scope.machineinfo = {};
        $scope.numeral = numeral;

        var updateMachineSizes = function(){
        	$scope.machineinfo = {};
        	_.each($scope.machines, function(element, index, list){
        		$scope.machineinfo[element.id] = {};
        		size = _.findWhere($scope.sizes, { id: element.sizeId });
        		$scope.machineinfo[element.id]['size'] = size;
                image = _.findWhere($scope.images, { id: element.imageId });
                $scope.machineinfo[element.id]['image'] = image;
                $scope.machineinfo[element.id]['storage'] = element.storage;
        		}
        	)

        };

        $scope.$watch('machines', updateMachineSizes);
        $scope.$watch('sizes', updateMachineSizes, true);
        $scope.$watch('images', updateMachineSizes, true);

    }
]);
