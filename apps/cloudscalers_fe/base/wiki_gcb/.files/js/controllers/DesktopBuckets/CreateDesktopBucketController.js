angular.module('cloudscalers.controllers')
    .controller('CreateDesktopBucketController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            projectName: '',
            users: [],
            newUser: { email: '', userType: '', id: Math.random() },
            storage: 100,
            locations: [false, false, false],
            numOfficeLicenses: 5,
            numFullOfficeLicenses: 0,

            addNewUser: function() {
                this.users.push(this.newUser);
                this.newUser = { email: '', userType: '', id: Math.random() };
                location.path('');
            },

            isValid: function() {
                return this.projectName && this.storage;
            }
        };

        $scope.save = function() {
            DesktopBucketService.save($scope.bucket);
            location.href = "My Desktop Buckets";
        };
    }])