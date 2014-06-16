angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', '$modal', 'CloudSpace', 'LoadingDialog','$timeout', '$ErrorResponseAlert',
        function ($scope, $modal, CloudSpace, LoadingDialog, $timeout, $ErrorResponseAlert) {
            $scope.isCollapsed = true;

            $scope.AccountCloudSpaceHierarchy = undefined;

            var buildAccountCloudSpaceHierarchy = function () {
                var cloudspacesGroups = _.groupBy($scope.cloudspaces, 'accountId');
//		console.log($scope.cloudspaces);
		console.log(cloudspacesGroups);
		console.log($scope.accounts);
                $scope.AccountCloudSpaceHierarchy = _.map($scope.accounts, function (account) {
                account.cloudspaces = cloudspacesGroups;
//		    console.log(account.id);
                    return account;
                });
//		console.log($scope.AccountCloudSpaceHierarchy);
            }

            $scope.$watch('accounts', function () {
                buildAccountCloudSpaceHierarchy();
            });

            $scope.$watch('cloudspaces', function () {
                buildAccountCloudSpaceHierarchy();
            });

            var CreateCloudSpaceController = function ($scope, $modalInstance) {
                $scope.newCloudSpace = {
                    name: '',
                    account: $scope.currentAccount
                };
                $scope.submit = function () {
                    $modalInstance.close({
                        name: $scope.newCloudSpace.name,
                        accountId: $scope.newCloudSpace.account.id
                    });
                };
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };
            };
            $scope.createNewCloudSpace = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'createNewCloudSpaceDialog.html',
                    controller: CreateCloudSpaceController,
                    resolve: {},
                    scope: $scope
                });

                modalInstance.result.then(function (space) {
                    LoadingDialog.show('Creating cloudspace');
                    CloudSpace.create(space.name, space.accountId, $scope.currentUser.username).then(
                        function (cloudspaceId) {
                            //Wait a second, consistency on the api is not garanteed before that
                            $timeout(function(){
                                $scope.setCurrentCloudspace({name:space.name, id:cloudspaceId, accountId: space.accountId});
                                $scope.loadSpaces();
                                LoadingDialog.hide();
                            }, 1000);
                        },
                        function (reason) {
                            LoadingDialog.hide();
                            $ErrorResponseAlert(reason);
                        }
                    );
                });
            };
        }
    ]).filter('nospace', function () {
    return function (value) {
        return (!value) ? '' : value.replace(/ /g, '');
    };
});
