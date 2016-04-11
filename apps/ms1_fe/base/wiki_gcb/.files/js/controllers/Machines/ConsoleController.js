(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('ConsoleController', ConsoleController);

  function ConsoleController($scope, $routeParams, Machine) {
    $scope.machineConsoleUrlResult = {};
    $scope.novncConnectionInfo = {};
    $scope.sendText = sendText;

    $scope.$watch('tabactive.console+$parent.machine.status', tabActiveConsoleAndMachineStatus);
    //Make sure the keyboard is not captured when going to other pages
    $scope.$on('$destroy', destroy);
    $scope.$watch('machineConsoleUrlResult', machineConsoleUrlResult, true);

    function tabActiveConsoleAndMachineStatus() {
      if ($scope.tabactive.console && $scope.$parent.machine.status === 'RUNNING') {
        $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
      } else {
        $scope.machineConsoleUrlResult = {};
      }
    }

    function destroy() {
      $scope.machineConsoleUrlResult = {};
    }

    function sendText(rfb, text) {
      for (var i = 0; i < text.length; i++) {
        rfb.sendKey(text.charCodeAt(i));
      }
    }

    function machineConsoleUrlResult(newvalue) {
      if (newvalue.url) {
        var newConnectionInfo = {};
        var consoleUri = URI(newvalue.url);
        newConnectionInfo.host = consoleUri.hostname();
        newConnectionInfo.port = consoleUri.port();

        if (newConnectionInfo.port === '') {
          if (consoleUri.protocol() === 'http') {
            newConnectionInfo.port = '80';
          } else if (consoleUri.protocol() === 'https') {
            newConnectionInfo.port = '443';
          }
        }

        var token = consoleUri.search(true)['token'];
        newConnectionInfo.path = 'websockify?token=' + token;

        $scope.novncConnectionInfo = newConnectionInfo;
      } else {
        $scope.novncConnectionInfo = {};
      }
    }
  }
})();
