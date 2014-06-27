angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', '$modal', 'CloudSpace', 'LoadingDialog','$timeout', '$ErrorResponseAlert',
        function ($scope, $modal, CloudSpace, LoadingDialog, $timeout, $ErrorResponseAlert) {
            $scope.isCollapsed = true;

            $scope.AccountCloudSpaceHierarchy = undefined;

            var buildAccountCloudSpaceHierarchy = function () {
                var cloudspacesGroups = _.groupBy($scope.cloudspaces, 'accountId');
                var accountCloudSpaceHierarchy = []
                for (accountId in cloudspacesGroups){
                    var account = {id:accountId, name:cloudspacesGroups[accountId][0]['accountName']}
                    if 'accountAcl' in cloudspacesGroups[accountId][0]:
                    	account.acl = cloudspacesGroups[accountId][0]['accountAcl']
                    account.cloudspaces = cloudspacesGroups[accountId];
                    accountCloudSpaceHierarchy.push(account);
                }
                $scope.AccountCloudSpaceHierarchy = accountCloudSpaceHierarchy;
            }

            $scope.$watch('cloudspaces', function () {
                buildAccountCloudSpaceHierarchy();
            });

            var CreateCloudSpaceController = function ($scope, $modalInstance) {
                $scope.accounts = _.filter($scope.AccountCloudSpaceHierarchy,
                		function(account){return account.acl != null;}
                	);
                var selectedAccount = _.find($scope.accounts, function(account1,account2){return account1.id == account2.id;});
                if selectedAccount == null:
                	selectedAccount = $scope.accounts[0];
                
            	$scope.newCloudSpace = {
                    name: '',
                    account: selectedAccount
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
