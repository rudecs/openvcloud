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
            // Make tabs work
            $('.nav-tabs a').click(function(e) { $(this).tab('show'); e.preventDefault();})
            try {
                createGauge('jGauge1', 50, 0, 100, 300);
                createGauge('jGauge2', 1.6, 0, 12, 300);
                createGauge('jGauge3', 1.6, 0, 12, 300);
                createGauge('jGauge4', 1.6, 0, 12, 300);
            } catch(e) {}
        }, 0);
    }]);