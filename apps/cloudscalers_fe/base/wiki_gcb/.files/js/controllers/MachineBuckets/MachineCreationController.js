angular.module('cloudscalers.controllers')
    .controller('MachineCreationController', ['$scope', '$timeout', '$location', '$window', 'Machine', '$alert', '$rootScope', 'LoadingDialog', function($scope, $timeout, $location, $window, Machine, $alert, $rootScope, LoadingDialog) {
        $scope.machine = {
            name: '',
            description: '',
            sizeId: '',
            imageId: '',
            disksize: ''
        };

        $scope.sizepredicate = 'vcpus'
        $scope.groupedImages = [];
        $scope.availableDiskSizes = [10 ,20, 30, 40, 50, 100, 250, 500, 1000]        

        $scope.$watch('images', function() {
            _.extend($scope.groupedImages, _.pairs(_.groupBy($scope.images, function(img) { return img.type; })));
        }, true);

        $scope.$watch('sizes', function() {
            $scope.machine.sizeId = _.min($scope.sizes, function(size) { return size.vcpus;}).id;
        }, true);


        $scope.$watch('machine.imageId', function() {
            machinedisksize = _.findWhere($scope.images, {id:parseInt($scope.machine.imageId)});
            if (machinedisksize != undefined){
                size = _.find($scope.availableDiskSizes, function(size) { return  machinedisksize.size <= size;});
                $scope.machine.disksize =  size;
            }
        }, true);



        $scope.createredirect = function(id) {
            $location.path('/edit/' + id + '/console');
        };

        $scope.createError = function(response){
            $alert('A error has occured. <p><p>' + "    "
                +response.data.backtrace)
            console.log(response);
        }

        $scope.saveNewMachine = function() {
            LoadingDialog.show('Creating')
            Machine.create($scope.currentSpace.id, $scope.machine.name, $scope.machine.description, 
                           $scope.machine.sizeId, $scope.machine.imageId, $scope.machine.disksize,
                           $scope.machine.archive,
                           $scope.machine.region, $scope.machine.replication)
            .then(
                function(result){
                    LoadingDialog.hide();
                    $scope.createredirect(result);
                },
                function(reason){
                    LoadingDialog.hide();
                    $scope.createError(reason);
                }
            );
        };

        $scope.showDiskSize = function(disksize) {
            machinedisksize = _.findWhere($scope.images, {id:parseInt($scope.machine.imageId)});
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
