cloudscalersControllers
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