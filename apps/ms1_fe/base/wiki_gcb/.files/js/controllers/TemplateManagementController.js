(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('TemplateManagementController', TemplateManagementController);

  function TemplateManagementController($scope, Account, Image) {
      $scope.filteredTemplates = [];
      $scope.templates = Image.list($scope.currentAccount.id);

      //Binding and Watch
      $scope.$watch('templates', template, true);

      // Function
      function template() {
        $scope.filteredTemplates = _.where($scope.templates, {'type': 'Custom Templates'});
      }
    }
})();
