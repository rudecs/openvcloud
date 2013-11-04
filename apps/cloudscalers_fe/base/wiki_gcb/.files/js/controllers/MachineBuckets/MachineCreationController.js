cloudscalersControllers
    .controller('MachineCreationController', ['$scope', '$timeout', '$location', '$window', 'Machine', 'Size', 'Image', function($scope, $timeout, $location, $window, Machine, Size, Image) {
        $scope.machine = {
            cloudspaceId: 1,
            name: '',
            description: '',
            sizeId: '',
            imageId: ''
        };

        $scope.sizes = Size.list();
        $scope.images = Image.list();
        $scope.numeral = $window.numeral;
        $scope.sizepredicate = 'vcpus'
        $scope.groupedImages = [];        

        $scope.$watch('images', function() {
            _.extend($scope.groupedImages, _.pairs(_.groupBy($scope.images, function(img) { return img.type; })));
        }, true);


        $scope.saveNewMachine = function() {
            Machine.create($scope.machine.cloudspaceId, $scope.machine.name, $scope.machine.description, 
                           $scope.machine.sizeId, $scope.machine.imageId, $scope.machine.disksize,
                           $scope.machine.archive,
                           $scope.machine.region, $scope.machine.replication);
            $location.path('/list');
        };

        $scope.showDiskSize = function(disksize) {
            machinedisksize = _.findWhere($scope.images, {id:parseInt($scope.machine.imageId)});
            console.log('executing showDiskSize')
            if (machinedisksize === undefined){
                return true;
            }
            if(machinedisksize.size <= disksize){
               return false;
            }
            else{
               return true;
           }
       };

        $scope.isValid = function() {
            return $scope.machine.name !== '' && $scope.machine.sizeId !== '' && $scope.machine.imageId !== '';
        };
    }]);
