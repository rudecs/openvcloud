


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
    }])

    .controller('BucketNewCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.bucket = new MachineBucket(Buckets,
        {
            id: Math.random() * 1000000000,
            ip: generateIp(),
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
        });

        $scope.saveBucket = function() {
            $scope.bucket.add();
            location.href = "#/list";
        };
    }])

    .controller('BucketEditCtrl', ['$scope', '$routeParams', '$location', 'Buckets', '$timeout', function($scope, $routeParams, $location, Buckets, $timeout) {
        $scope.bucket = Buckets.getById(parseFloat($routeParams.bucketId));
        $scope.newSnapshot = {name: '', date: getFormattedDate()};
        $scope.cloneName = '';
        $scope.selectedSnapshot = '';
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
            $scope.bucket.restoreSnapshot(snapshot);
            location.reload();
        };

        $scope.createSnapshot = function() {
            $scope.bucket.createSnapshot($scope.newSnapshot.name);
            $scope.newSnapshot = {name: '', date: getFormattedDate()};
            $scope.closeSnapshotModal();
            showLoading('Creating a snapshot');
        };

        $scope.cloneBucket = function() {
            $scope.bucket.clone($scope.cloneName);
            $scope.closeCloneModal();
            $location.path("/list/");
        };

        $scope.boot = function() {
            $scope.bucket.boot();
            showLoading('Starting machine');
        }

        $scope.powerOff = function() {
            $scope.bucket.powerOff();
            showLoading('Stopping machine');
        };

        $scope.pause = function() {
            $scope.bucket.pause();
            showLoading('Pausing machine');
        };

        $scope.resize = function() {
            $scope.bucket.resize();
            showLoading('Changing package');
        };

        $scope.remove = function() {
            if (confirm('Are you sure you want to destroy this bucket?')) {
                $scope.bucket.remove();
                location.href = "#/list";
            }
        };

        $scope.rename = function() {
            if (this.oldName)
                this.bucket.name = this.oldName;
            $scope.bucket.save();
            $scope.closeRenameModal();
            showLoading('Renaming machine');
        };

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
    }])
