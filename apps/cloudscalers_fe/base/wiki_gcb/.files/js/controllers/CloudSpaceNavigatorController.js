angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', '$modal', 'CloudSpace', 'LoadingDialog','$timeout',
        function ($scope, $modal, CloudSpace, LoadingDialog, $timeout) {
            $scope.isCollapsed = true;

            $scope.AccountCloudSpaceHierarchy = undefined;

            var buildAccountCloudSpaceHierarchy = function () {
                var cloudspacesGroups = _.groupBy($scope.cloudspaces, 'accountId');
                $scope.AccountCloudSpaceHierarchy = _.map($scope.accounts, function (account) {
                    account.cloudspaces = cloudspacesGroups[account.id];
                    return account;
                });
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
                        function (result) {
                            LoadingDialog.hide();
                            //TODO: show error
                        }
                    );
                });
            };
        }
    ]);