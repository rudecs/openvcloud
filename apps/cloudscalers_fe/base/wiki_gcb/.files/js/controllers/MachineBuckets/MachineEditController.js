cloudscalersControllers
    .controller('MachineEditController', ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'confirm', function($scope, $routeParams, $timeout, $location, Machine, confirm) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.snapshots = Machine.listSnapshots($routeParams.machineId);
        $scope.newSnapshotName = '';

        $scope.destroy = function() {
            if (confirm('Are you sure you want to destroy this bucket?')) {
                Machine.delete($scope.machine.id);
                $location.path("/list");
            }
        };

        $scope.createSnapshot = function() {
            $scope.closeSnapshotModal();
            Machine.createSnapshot($scope.machine.id, $scope.newSnapshotName);
            $scope.newSnapshotName = '';
            showLoading('Creating a snapshot');
        };

        $scope.showSnapshotModal = function() {
            $scope.snapshotModalOpen = true;
        };

        $scope.closeSnapshotModal = function() {
            $scope.snapshotModalOpen = false;
        };

        // The existing jgauge macros uses jQuery. Because of the way AngularJS works, code executed using 
        // $document.ready will not work as expected. This is one way to do it.
        $timeout(function(){
            try {
                // Make tabs work
                $('.nav-tabs a').click(function(e) { $(this).tab('show'); e.preventDefault();})

                myGauge1.init();
                myGauge1.setValue(100)
                setInterval('randVal1()', 3000);

                myGauge2.init();
                myGauge2.setValue(60)
                setInterval('randVal2()', 3000);
                
                myGauge3.init();
                myGauge3.setValue(60)
                setInterval('randVal3()', 3000);
                
                myGauge4.init();
                myGauge4.setValue(60)
                setInterval('randVal4()', 3000);
            } catch(e) {}
        }, 0);
    }]);