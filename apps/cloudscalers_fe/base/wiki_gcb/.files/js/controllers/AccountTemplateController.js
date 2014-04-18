angular.module('cloudscalers.controllers')
    .controller('AccountTemplateController', ['$scope', 'Account', 'Image', function($scope, Account, Image) {
      $scope.filteredTemplates = []
      $scope.templates =  Image.list($scope.currentAccount.id);
      $scope.$watch('templates',  function(){
              $scope.filteredTemplates = _.where($scope.templates, {"type": "custom templates"});
              console.log($scope.filteredTemplates);
            }, true);
    }]);