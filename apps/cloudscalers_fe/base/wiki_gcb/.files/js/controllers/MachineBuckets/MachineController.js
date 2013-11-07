
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', 'Size', 'Image', function($scope, Machine, Size, Image) {
        $scope.machines = Machine.list(1);
        $scope.sizes = Size.list();
        $scope.images = Image.list();
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

        $scope.$watch('machines', updateMachineSizes, true);
        $scope.$watch('sizes', updateMachineSizes, true);
        $scope.$watch('images', updateMachineSizes, true);

    }
]);
