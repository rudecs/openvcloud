'use strict';

function getFormattedDate() {
    var d = new Date();
    return d.getFullYear() + "-" + d.getMonth() + "-" + d.getDay() + " " + d.getHours() + ":" + d.getMinutes();
}

angular.module('myApp.controllers', ['ui.bootstrap'])

    .controller('BucketListCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.buckets = Buckets.getAll();
    }])

    .controller('BucketNewCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            ip: Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256),
            name: '',
            plan: '',
            region: '',
            status: 'Running',
            image: '',
            history: []
        };
  
        $scope.bucketValid = function() {
            return $scope.bucket.name && $scope.bucket.plan && $scope.bucket.region && $scope.bucket.image;
        };

        $scope.saveBucket = function() {
            $scope.bucket.history.push({event: 'Created', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.add($scope.bucket);
            location.href = "#/list";
        };
    }])

    .controller('BucketEditCtrl', ['$scope', '$routeParams', 'Buckets', 'Snapshots', function($scope, $routeParams, Buckets, Snapshots) {
        $scope.bucket = Buckets.getById(parseFloat($routeParams.bucketId));
        $scope.snapshots = Snapshots.getAll();
        $scope.newSnapshot = {name: ''};
        $scope.selectedSnapshot = '';

        $scope.bucket.boot = function() {
            $scope.bucket.status = 'Running';
            $scope.bucket.history.push({event: 'Booted', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
        };

        $scope.bucket.powerOff = function() {
            $scope.bucket.status = 'Halted';
            $scope.bucket.history.push({event: 'Powered off', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
        };

        $scope.bucket.resize = function() {
            $scope.bucket.history.push({event: 'Bucket resized', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
        };

        $scope.bucket.remove = function() {
            if (confirm('Are you sure you want to destroy this droplet?')) {
                Buckets.remove($scope.bucket);
                location.href = "#/list";
            }
        };

        $scope.bucket.save = function() {
            Buckets.save($scope.bucket);
        }

        $scope.restoreSnapshot = function() {
            // Real implementation will call Snapshots.restoreSnapshot(), but for now we just reload
            location.reload();
        };

        $scope.createSnapshot = function() {
            Snapshots.add($scope.newSnapshot);
            $scope.snapshots = Snapshots.getAll();
            $scope.newSnapshot = {name: ''};
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
            }
        };

        $scope.create = function() {
            DesktopBucketService.add($scope.bucket);
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
    }]);