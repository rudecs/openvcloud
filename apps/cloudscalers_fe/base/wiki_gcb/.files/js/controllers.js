'use strict';

function getFormattedDate() {
    var d = new Date();
    return d.getFullYear() + "-" + d.getMonth() + "-" + d.getDay() + " " + d.getHours() + ":" + d.getMinutes();
}

angular.module('myApp.controllers', ['ui.bootstrap'])

    .controller('BucketListCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.buckets = Buckets.getAll();
    }])

    .controller('BucketNewCtrl', ['$scope', 'Buckets', '$location', function($scope, Buckets) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            name: '',
            plan: '',
            region: '',
            status: 'active',
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
            $scope.bucket.status = 'active';
            $scope.bucket.history.push({event: 'Booted', initiated: getFormattedDate(), user: 'John Q.'})
            Buckets.save($scope.bucket);
        };

        $scope.bucket.powerOff = function() {
            $scope.bucket.status = 'off';
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

    }]);