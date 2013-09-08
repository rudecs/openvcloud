'use strict';

function getFormattedDate() {
    var d = new Date();
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDay() + " " + d.getHours() + ":" + d.getMinutes();
}

function showLoading() {
    $('#create-ssh').show('fast');
    setTimeout(function() {
        $('#create-ssh').hide('fast');
    }, 3000);
}

angular.module('myApp.controllers', ['ui.bootstrap'])

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
            history: []
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
            $scope.bucket.history.push({event: 'Created', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.add($scope.bucket);
            location.href = "#/list";
        };
    }])

    .controller('BucketEditCtrl', ['$scope', '$routeParams', '$location', 'Buckets', 'Snapshots', '$timeout', function($scope, $routeParams, $location, Buckets, Snapshots, $timeout) {
        $scope.bucket = Buckets.getById(parseFloat($routeParams.bucketId));
        $scope.snapshots = Snapshots.getAll();
        $scope.newSnapshot = {name: '', date: getFormattedDate()};
        $scope.cloneName = '';
        $scope.selectedSnapshot = '';

        // AFAIK, this is the way to execute code when the view is finished loading. Here I use it to initialize the gauge
        $timeout(function(){
                    myGauge1.init();
                    myGauge1.setValue(60)
                    setInterval('randVal1()', 3000);

        }, 0);

        $scope.$watch('plan + additionalStorage', function() {
            $scope.bucket.cpu = $scope.bucket.plan.cpu;
            $scope.bucket.memory = $scope.bucket.plan.memory;
            $scope.bucket.storage = $scope.bucket.plan.storage + $scope.bucket.additionalStorage;
        });

        $scope.bucket.boot = function() {
            $scope.bucket.status = 'Running';
            $scope.bucket.history.push({event: 'Started', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
            showLoading();
        };

        $scope.bucket.powerOff = function() {
            $scope.bucket.status = 'Halted';
            $scope.bucket.history.push({event: 'Powered off', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
            showLoading();
        };

        $scope.bucket.pause = function() {
            $scope.bucket.status = 'Paused';
            $scope.bucket.history.push({event: 'Paused', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
            showLoading();
        };

        $scope.bucket.resize = function() {
            $scope.bucket.history.push({event: 'Bucket resized', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
            showLoading();
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
            showLoading();
        };

        $scope.bucket.save = function() {
            Buckets.save($scope.bucket);
            $scope.renameModalOpen = false;
            showLoading();
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

        $scope.restoreSnapshot = function() {
            // Real implementation will call Snapshots.restoreSnapshot(), but for now we just reload
            //location.reload();
            showLoading();
        };

        $scope.createSnapshot = function() {
            Snapshots.add($scope.newSnapshot);
            $scope.snapshots = Snapshots.getAll();
            $scope.newSnapshot = {name: '', date: getFormattedDate()};
            $scope.closeSnapshotModal();
            showLoading();
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
                history: [{event: 'Created', initiated: getFormattedDate(), user: 'John Q.'}]
            });

            $scope.closeCloneModal();
            $location.path("/list/");
        };
    }])

    .controller('SettingsController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: '',
                email: '',
                // password: '', // Passwords must not be saved locally
                //ccType: '',
                //ccNum: '',
                //ccExpiration: '',
                //ccv: ''
            };
        } else {
            settings = settings[0];
        }
        $scope.settings = settings;

        $scope.save = function() {
            $scope.settings.password = $scope.password;
            $scope.settings.ccNum = $scope.ccNum;
            $scope.settings.ccType = $scope.ccType;
            $scope.settings.ccExpiration = $scope.ccExpiration;
            $scope.settings.ccv = $scope.ccv;

            SettingsService.save($scope.settings);
        }
    }])

    .controller('CreateDesktopBucketController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            projectName: '',
            users: [],
            newUser: { email: '', userType: '' },
            storage: 100,
            locations: [false, false, false],
            numOfficeLicenses: 5,
            numFullOfficeLicenses: 0,

            addNewUser: function() {
                this.users.push(this.newUser);
                this.newUser = { email: '', userType: '' };
            },

            isValid: function() {
                return this.projectName && this.users.length > 0 && this.storage;
            }
        };

        $scope.create = function() {
            DesktopBucketService.add($scope.bucket);
            location.href = "My Desktop Buckets";
        };
    }])

    .controller('ListDesktopBucketsController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.buckets = DesktopBucketService.getAll();
        $scope.numOfDataLocations = function(bucket) {
            var numOfLocations = 0;
            for (var i = 0; i < bucket.locations.length; i++) {
                if (bucket.locations[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        }
    }])

    .controller('EditDesktopBucketController', ['$scope', '$routeParams', 'DesktopBucketService', function($scope, $routeParams, DesktopBucketService) {
        $scope.bucket = DesktopBucketService.getById(parseFloat(location.hash.substr(2)));

        $scope.bucket.isValid = function() {
            return this.projectName && this.users.length > 0 && this.storage;
        };

        $scope.bucket.addNewUser = function() {
            this.users.push(this.newUser);
            this.newUser = { email: '', userType: '' };
        };

        $scope.update = function() {
            DesktopBucketService.save($scope.bucket);
            location.href = "My Desktop Buckets"
        };
    }])

    .controller('SupportController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: 'User name',
                email: 'email@site.com',
                credit: 50,
                creditHistory: [],
                // password: '', // Passwords must not be saved locally
                //ccType: '',
                //ccNum: '',
                //ccExpiration: '',
                //ccv: ''
            };
        } else {
            settings = settings[0];
        }
        $scope.settings = settings;
    }])

    .controller('BillingController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: 'User name',
                email: 'email@site.com',
                credit: 50,
                creditHistory: [],
                addedAmount: 0,
                // password: '', // Passwords must not be saved locally
                //ccType: '',
                //ccNum: '',
                //ccExpiration: '',
                //ccv: ''
            };
        } else {
            settings = settings[0];
        }
        $scope.settings = settings;
        $scope.addedAmount = 0;

        $scope.add = function() {
            if (!$scope.addedAmount || $scope.addedAmount <= 0)
                return;
            $scope.settings.credit += $scope.addedAmount;
            $scope.settings.creditHistory.push({date: getFormattedDate(), description: 'Payment', amount: $scope.addedAmount});
            SettingsService.save($scope.settings);
            showLoading();
        };
    }]);
