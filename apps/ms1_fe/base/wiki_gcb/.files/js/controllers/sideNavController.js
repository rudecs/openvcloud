angular.module('cloudscalers.controllers')
    .controller('sideNavController', ['$scope', 'Networks', 'Machine', '$modal', '$interval','$ErrorResponseAlert','LoadingDialog', 'CloudSpace','$timeout', '$routeParams', '$window' ,
        function ($scope, Networks, Machine, $modal, $interval,$ErrorResponseAlert,LoadingDialog, CloudSpace,$timeout, $routeParams, $window) {

            $scope.$watch('currentSpace.acl', function () {
                if($scope.currentUser.username && $scope.currentSpace.acl && !$scope.currentUserAccessrightOnCloudSpace){
                    var currentUserAccessright =  _.find($scope.currentSpace.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; }).right.toUpperCase();
                    if(currentUserAccessright == "R"){
                        $scope.currentUserAccessrightOnCloudSpace = 'Read';
                    }else if( currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') == -1 && currentUserAccessright.indexOf('U') == -1){
                        $scope.currentUserAccessrightOnCloudSpace = "ReadWrite";
                    }else if(currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') != -1 && currentUserAccessright.indexOf('U') != -1){
                        $scope.currentUserAccessrightOnCloudSpace = "Admin";
                    }
                }
            });


        }]);