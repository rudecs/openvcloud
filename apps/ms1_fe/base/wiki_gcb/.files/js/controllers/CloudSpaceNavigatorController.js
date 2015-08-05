angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', '$modal', 'LocationsService', 'CloudSpace', 'LoadingDialog','$timeout', '$ErrorResponseAlert', '$window',
        function ($scope, $modal, LocationsService, CloudSpace, LoadingDialog, $timeout, $ErrorResponseAlert, $window) {
            $scope.isCollapsed = true;

            $scope.locations = {};
            
            LocationsService.list().then(function(locations) {
                $scope.locations = locations;
            });

            $scope.AccountCloudSpaceHierarchy = undefined;

            var buildAccountCloudSpaceHierarchy = function () {
                var cloudspacesGroups = _.groupBy($scope.cloudspaces, 'accountId');
                var accountCloudSpaceHierarchy = [];
                for (accountId in cloudspacesGroups){
                    var firstCloudSpace = cloudspacesGroups[accountId][0];
                    var account = {id:accountId, name:firstCloudSpace['accountName'], DCLocation:firstCloudSpace['accountDCLocation'] }
                    if ('accountAcl' in firstCloudSpace){
                        account.acl = firstCloudSpace['accountAcl']
                    }
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


                var selectedAccount = _.find($scope.accounts, function(account1){return account1.id == $scope.currentAccount.id;});
                if (selectedAccount == null){
                    selectedAccount = $scope.accounts[0];
                }
                $scope.newCloudSpace = {
                    name: '',
                    account: selectedAccount
                };
                $scope.submit = function () {
                    $modalInstance.close({
                        name: $scope.newCloudSpace.name,
                        accountId: $scope.newCloudSpace.account.id,
                        selectedLocation: $scope.selectedLocation
                    });
                };
                $scope.cancel = function () {
                    $modalInstance.dismiss('cancel');
                };

                $scope.selectedLocation = $scope.locations[0].locationCode;

                $scope.changeLocation = function(location) {
                    $scope.selectedLocation = location.locationCode;
                };

                if($scope.accounts.length == 0){
                    $modalInstance.close({
                        name: "",
                        accountId: "",
                        selectedLocation: ""
                    });
                    $timeout(function(){
                        angular.element('.new-cloudspace-modal').hide();
                        angular.element("#cloudspacesListEmptyDialog").modal("show");
                    });
                }
            };
            $scope.createNewCloudSpace = function () {
                var modalInstance = $modal.open({
                    templateUrl: 'createNewCloudSpaceDialog.html',
                    controller: CreateCloudSpaceController,
                    resolve: {},
                    scope: $scope,
                    backdrop : 'static'
                });

                modalInstance.result.then(function (space) {
                        LoadingDialog.show('Creating cloudspace');
                        CloudSpace.create(space.name, space.accountId, $scope.currentUser.username, space.selectedLocation).then(
                            function (cloudspaceId) {
                                //Wait a second, consistency on the api is not garanteed before that
                                $timeout(function(){
                                    var ua = window.navigator.userAgent;
                                    var msie = ua.indexOf("MSIE ");
                                    if (msie > 0){
                                        $window.location.reload();
                                    }
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
