
cloudscalersControllers
    .controller('MachineController', ['$scope', 'Machine', 'Size', 'Image', function($scope, Machine, Size, Image) {
        $scope.machines = Machine.list(1);
        $scope.sizes = Size.list();
        $scope.images = Image.list();

        $scope.getMemory = function(machine) {
                var size = _.findWhere($scope.sizes, { id: machine.sizeId });
                return size ? numeral(size.memory * 1024 * 1024).format('0 b') : 'N/A';
        }
    }]);
