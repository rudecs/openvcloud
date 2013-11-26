
angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', function($scope) {
        $scope.isCollapsed = true;
        
        $scope.AccountCloudSpaceHierarchy = undefined;
        
        var buildAccountCloudSpaceHierarchy = function(){

          var cloudspacesGroups = _.groupBy($scope.cloudspaces, 'accountId');
          $scope.AccountCloudSpaceHierarchy = _.map($scope.accounts, function(account) { 
              account.cloudspaces = cloudspacesGroups[account.id]; 
              return account;
          });
          
        }
        
        $scope.$watch('accounts',function(){
          buildAccountCloudSpaceHierarchy();
        });
        
        $scope.$watch('cloudspaces', function(){
        	buildAccountCloudSpaceHierarchy();
        });
        
        
    }]);
