
function getSnapshot(bucket) {
    // $watch doesn't always update the values. This is why I need to recalculate here.
    return {
        name: bucket.name + '_' + getFormattedDate(), // TODO: change
        cpu: bucket.plan.cpu,
        memory: bucket.plan.memory,
        storage: bucket.plan.storage,
        additionalStorage: bucket.additionalStorage
    };
}

myAppControllers
    .controller('BucketListCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.buckets = Buckets.getAll();
        
        $scope.numOfDataLocations = function(bucket) {
            var numOfLocations = 0;
            for (var i = 0; i < bucket.region.length; i++) {
                if (bucket.region[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        };

        $scope.$watch('buckets', function() {
            for (var i = 0; i < $scope.buckets.length; i++) {
                try {
                    var bucket = $scope.buckets[i];
                    bucket.cpu = bucket.plan.cpu;
                    bucket.memory = bucket.plan.memory;
                    bucket.storage = bucket.plan.storage + bucket.additionalStorage;
                } catch(e) {}
            }
        }, true);
    }])

    .controller('BucketNewCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            ip: Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256),
            name: '',
            plan: {},
            additionalStorage: 0,

            cpu: 1,
            memory: 1,
            storage: 10,
            
            region: [false, false, false],
            status: 'Running',
            image: '',
            history: [],
            snapshots: []
        };

        $scope.$watch('plan + additionalStorage', function() {
            $scope.bucket.cpu = $scope.bucket.plan.cpu;
            $scope.bucket.memory = $scope.bucket.plan.memory;
            $scope.bucket.storage = $scope.bucket.plan.storage + $scope.bucket.additionalStorage;
        });
  
        $scope.bucketValid = function() {
            return $scope.bucket.name && $scope.bucket.plan && $scope.bucket.region && $scope.bucket.image;
        };

        $scope.saveBucket = function() {
            $scope.bucket.snapshots.push(getSnapshot($scope.bucket));
            $scope.bucket.history.push({event: 'Created', initiated: getFormattedDate(), user: 'Admin'})
            Buckets.add($scope.bucket);
            location.href = "#/list";
        };
    }])

    .controller('BucketEditCtrl', ['$scope', '$routeParams', '$location', 'Buckets', '$timeout', function($scope, $routeParams, $location, Buckets, $timeout) {
        $scope.bucket = Buckets.getById(parseFloat($routeParams.bucketId));
        $scope.newSnapshot = {name: '', date: getFormattedDate()};
        $scope.cloneName = '';
        $scope.selectedSnapshot = '';

        // AFAIK, this is the way to execute code when the view is finished loading. Here I use it to initialize the gauge
        $timeout(function(){
                    myGauge1.init();
                    myGauge1.setValue(60)
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
        }, 0);

        $scope.$watch('plan + additionalStorage', function() {
            $scope.bucket.cpu = $scope.bucket.plan.cpu;
            $scope.bucket.memory = $scope.bucket.plan.memory;
            $scope.bucket.storage = $scope.bucket.plan.storage + $scope.bucket.additionalStorage;
        });

        $scope.bucket.locations = function() {
            // TODO: Get list of regions from a single source
            return ["Ghent, Belgium", "Bruges, Belgium", "Lenoir, NC, USA"]
                .filter(function(element, index) { return $scope.bucket.region[index]; })
                .join(" - ");
        }

        $scope.bucket.boot = function() {
            $scope.bucket.status = 'Running';
            $scope.bucket.history.push({event: 'Started', initiated: getFormattedDate(), user: 'Admin'})
            Buckets.save($scope.bucket);
            showLoading('Starting machine');
        };

        $scope.bucket.powerOff = function() {
            $scope.bucket.status = 'Halted';
            $scope.bucket.history.push({event: 'Powered off', initiated: getFormattedDate(), user: 'Admin'})
            Buckets.save($scope.bucket);
            showLoading('Stopping machine');
        };

        $scope.bucket.pause = function() {
            $scope.bucket.status = 'Paused';
            $scope.bucket.history.push({event: 'Paused', initiated: getFormattedDate(), user: 'Admin'})
            Buckets.save($scope.bucket);
            showLoading('Pausing machine');
        };

        $scope.bucket.resize = function() {
            $scope.bucket.history.push({event: 'Bucket resized', initiated: getFormattedDate(), user: 'Admin'})
            Buckets.save($scope.bucket);
            showLoading('Changing package');
        };

        $scope.bucket.remove = function() {
            if (confirm('Are you sure you want to destroy this bucket?')) {
                Buckets.remove($scope.bucket);
                location.href = "#/list";
            }
        };

        $scope.bucket.rename = function() {
            if ($scope.bucket.oldName)
                $scope.bucket.name = $scope.bucket.oldName;
            $scope.bucket.save();
            showLoading('Renaming machine');
        };

        $scope.bucket.save = function() {
            Buckets.save($scope.bucket);
            $scope.renameModalOpen = false;
        };

        $scope.bucket.isValid = function() {
            return $scope.bucket.name && $scope.bucket.cpu && $scope.bucket.memory &&$scope.bucket.storage && $scope.bucket.region && $scope.bucket.image;
        };

        $scope.renameModalOpen = false;
        $scope.snapshotModalOpen = false;
        $scope.cloneModalOpen = false;
        $scope.modalOpts = {
            backdropFade: true,
            dialogFade: true
        };

        $scope.showRenameModal = function() {
            $scope.bucket.oldName = $scope.bucket.name;
            $scope.renameModalOpen = true;
        };

        $scope.closeRenameModal = function() {
            $scope.renameModalOpen = false;
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

        $scope.restoreSnapshot = function(snapshot) {
            $scope.bucket.plan.cpu = snapshot.cpu;
            $scope.bucket.plan.memory = snapshot.memory;
            $scope.bucket.plan.storage = snapshot.storage;
            $scope.bucket.additionalStorage = snapshot.additionalStorage;
            showLoading('Restoring snapshot');
        };

        $scope.createSnapshot = function() {
            var snapshot = getSnapshot($scope.bucket);
            snapshot.name = $scope.newSnapshot.name;
            $scope.bucket.snapshots.push(snapshot);
            Buckets.save($scope.bucket);
            $scope.newSnapshot = {name: '', date: getFormattedDate()};
            $scope.closeSnapshotModal();
            showLoading('Creating a snapshot');
        };

        $scope.cloneBucket = function() {
            var cloneId = Math.random() * 1000000000;
            Buckets.add({
                id: cloneId,
                ip: Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256),
                name: $scope.cloneName,
                cpu: $scope.bucket.cpu,
                memory: $scope.bucket.memory,
                storage: $scope.bucket.storage,
                region: $scope.bucket.region,
                status: 'Running',
                image: $scope.bucket.image,
                history: [{event: 'Created', initiated: getFormattedDate(), user: 'Admin'}]
            });

            $scope.closeCloneModal();
            $location.path("/list/");
        };
    }])
