angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', '$modal', 'CloudSpace',
        function ($scope, $modal, CloudSpace) {
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
                    CloudSpace.create(space.name, space.accountId, $scope.currentUser.id).then(
                        function (cloudspaceId) {
                            $scope.loadSpaces().then(function() {
                                buildAccountCloudSpaceHierarchy();
                                $scope.setCurrentCloudspace(_.findWhere($scope.cloudspaces, {id: cloudspaceId}));
                            });
                        },
                        function (result) {
                            //TODO: show error
                        }
                    );
                });
            }
        }
    ]);