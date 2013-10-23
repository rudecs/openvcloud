cloudscalersControllers
    .controller('MachineEditController', 
                ['$scope', '$routeParams', '$timeout', '$location', 'Machine', 'Image', 'Size', 'confirm', 
                function($scope, $routeParams, $timeout, $location, Machine, Image, Size, confirm) {
        $scope.machine = Machine.get($routeParams.machineId);
        $scope.machine.history = [{event: 'Created', initiated: getFormattedDate(), user: 'Admin'}];
        $scope.oldMachine = {};
        $scope.snapshots = Machine.listSnapshots($routeParams.machineId);
        $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
        $scope.newSnapshotName = '';
        $scope.cloneName = '';

        $scope.sizes = Size.list();
        $scope.images = Image.list();
        $scope.imagesList = [];

        $scope.$watch('images', function() {
            $scope.imagesList = _.flatten(_.values(_.object($scope.images)));
        });

        $scope.$on('machine:loaded', function() {
            angular.copy($scope.machine, $scope.oldMachine);
        });

        $scope.renameModalOpen = false;
        $scope.snapshotModalOpen = false;
        $scope.cloneModalOpen = false;

        $scope.destroy = function() {
            if (confirm('Are you sure you want to destroy this machine?')) {
                Machine.delete($scope.machine.id);
                $location.path("/list");
            }
        };

        $scope.createSnapshot = function() {
            $scope.machine.history.push({event: 'Created snapshot', initiated: getFormattedDate(), user: 'Admin'});
            $scope.closeSnapshotModal();
            Machine.createSnapshot($scope.machine.id, $scope.newSnapshotName);
            $scope.newSnapshotName = '';
            showLoading('Creating a snapshot');
        };

        $scope.restoreSnapshot = function(snapshot) {
            $scope.machine.history.push({event: 'Restored from snapshot', initiated: getFormattedDate(), user: 'Admin'});
            //$scope.machine.restoreSnapshot(snapshot);
            location.reload();
        };

        $scope.showSnapshotModal = function() {
            $scope.snapshotModalOpen = true;
        };

        $scope.closeSnapshotModal = function() {
            $scope.snapshotModalOpen = false;
        };

        $scope.showCloneModal = function() {
            $scope.cloneModalOpen = true;
        };

        $scope.closeCloneModal = function() {
            $scope.cloneModalOpen = false;
        };

        $scope.showRenameModal = function() {
            $scope.oldName = $scope.machine.name;
            $scope.renameModalOpen = true;
        };

        $scope.closeRenameModal = function() {
            $scope.renameModalOpen = false;
        };

        $scope.rename = function() {
            Machine.rename($scope.machine, $scope.oldName);
            $scope.closeRenameModal();
            showLoading('Renaming machine...');
        };

        $scope.cloneMachine = function() {
            Machine.clone($scope.machine, $scope.cloneName);
            $scope.closeCloneModal();
            $location.path("/list/");
            showLoading('Cloning...');
        };

        $scope.start = function() {
            $scope.machine.history.push({event: 'Started', initiated: getFormattedDate(), user: 'Admin'});
            Machine.start($scope.machine);
            showLoading('Starting...');
        };

         $scope.stop = function() {
            $scope.machine.history.push({event: 'Stopping machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.stop($scope.machine);
            showLoading('Stopping ...');
        };

        $scope.pause = function() {
            $scope.machine.history.push({event: 'Pausing machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.pause($scope.machine);
            showLoading('Pausing...');
        };

        $scope.resume = function() {
            $scope.machine.history.push({event: 'Resuming machine', initiated: getFormattedDate(), user: 'Admin'});
            Machine.resume($scope.machine);
            showLoading('Resuming...');
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