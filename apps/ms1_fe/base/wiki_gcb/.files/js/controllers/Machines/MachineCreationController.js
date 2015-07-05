angular.module('cloudscalers.controllers')
    .controller('MachineCreationController', ['$scope', '$timeout', '$location', '$window', 'Machine', '$rootScope', 'LoadingDialog','$ErrorResponseAlert', function($scope, $timeout, $location, $window, Machine, $rootScope, LoadingDialog,$ErrorResponseAlert) {
        $scope.machine = {
            name: '',
            description: '',
            sizeId: '',
            imageId: '',
            disksize: ''
        };

        $scope.sizepredicate = 'memory'
        $scope.groupedImages = [];

        $scope.$watch('images', function() {
            if($scope.images){
                $scope.machine.imageId = String($scope.images[0].id);
                _.extend($scope.groupedImages, _.pairs(_.groupBy($scope.images, function(img) { return img.type; })));
            }
        }, true);

        $scope.$watch('sizes', function() {
            $scope.machine.sizeId = _.min($scope.sizes, function(size) { return size.vcpus;}).id;
        }, true);


        $scope.$watch('machine.imageId', function() {
            if($scope.machine.imageId){
                $scope.packageDisks = [];
                var selectedImageSize = _.findWhere($scope.images, { id: parseInt($scope.machine.imageId)}).size;
                var disks = _.findWhere($scope.sizes, { id: $scope.machine.sizeId }).disks;
                for(var i = 0; i <= disks.length -1 ; i++){
                    if(disks[i] >= selectedImageSize){
                        $scope.packageDisks.push(disks[i]);
                    }
                }
                if($scope.packageDisks.length > 0){
                    $scope.packageDisks.sort(function (a, b) {
                        return a - b;
                    });
                    $scope.machine.disksize = $scope.packageDisks[0];
                }else{
                    $scope.machine.disksize = "";
                }

            }
        }, true);

        $scope.$watch('machine.sizeId', function() {
            if($scope.machine.sizeId){
                var disks = _.findWhere($scope.sizes, { id: $scope.machine.sizeId }).disks;
                if($scope.machine.imageId){
                    $scope.packageDisks = [];
                    var selectedImageSize = _.findWhere($scope.images, { id: parseInt($scope.machine.imageId)}).size;
                    for(var i = 0; i <= disks.length -1 ; i++){
                        if(disks[i] >= selectedImageSize){
                            $scope.packageDisks.push(disks[i]);
                        }
                    }
                }else{
                    $scope.packageDisks = disks;
                }
                if($scope.packageDisks.length > 0){
                    $scope.packageDisks.sort(function (a, b) {
                        return a - b;
                    });
                    $scope.machine.disksize = $scope.packageDisks[0];
                }else{
                    $scope.machine.disksize = "";
                }
            }

        }, true);

        $scope.activePackage = function(packageID) {
            elementClass = ".package-" + packageID;
            angular.element('.active-package').removeClass('active-package');
            angular.element('.packages').find(elementClass).addClass('active-package');
        }

        $scope.createredirect = function(id) {
            $location.path('/edit/' + id + '/console');
        };

        $scope.saveNewMachine = function() {
            LoadingDialog.show('Creating');
            Machine.create($scope.currentSpace.id, $scope.machine.name, $scope.machine.description,
                           $scope.machine.sizeId, $scope.machine.imageId, $scope.machine.disksize,
                           $scope.machine.archive,
                           $scope.machine.region, $scope.machine.replication)
            .then(
                function(result){
                    LoadingDialog.hide();
                    $scope.createredirect(result);
                    $scope.machines.push({ cloudspaceId: $scope.currentSpace.id, name: $scope.machine.name, description: $scope.machine.description,
                        sizeId: $scope.machine.sizeId, imageId: $scope.machine.imageId, disksize: $scope.machine.disksize,
                        archive: $scope.machine.archive,
                        region: $scope.machine.region, replication: $scope.machine.replication });
                },
                function(reason){
                    LoadingDialog.hide();
                    $ErrorResponseAlert(reason);
                }
            );
        };

        $scope.isValid = function() {
            return $scope.machine.name !== '' && $scope.machine.sizeId !== '' && $scope.machine.imageId !== '' && $scope.machine.disksize != "";
        };
    }]);
