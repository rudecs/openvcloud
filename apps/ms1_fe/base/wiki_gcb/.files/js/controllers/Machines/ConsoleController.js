angular.module('cloudscalers.controllers')
    .controller('ConsoleController', ['$scope','$routeParams', 'Machine', function($scope, $routeParams, Machine) {
        $scope.machineConsoleUrlResult = {};
        $scope.novnc_connectioninfo = {};


        $scope.$watch('tabactive.console+$parent.machine.status',function(){
            if ($scope.tabactive.console && $scope.$parent.machine.status == "RUNNING"){
                $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
            }
            else {
                $scope.machineConsoleUrlResult = {};
            }
        });

        //Make sure the keyboard is not captured when going to other pages
        $scope.$on(
                "$destroy",
                function( event ) {
                    $scope.machineConsoleUrlResult = {};
                }
            );

        $scope.sendText = function(rfb, text) {
            for (var i=0; i<text.length; i++){
                rfb.sendKey(text.charCodeAt(i));
            }
        };

        $scope.$watch('machineConsoleUrlResult',function(newvalue, oldvalue){
            if (newvalue.url){
                var new_connection_info = {};
                console_uri = URI(newvalue.url);
                new_connection_info.host = console_uri.hostname();
                new_connection_info.port = console_uri.port();
                if (new_connection_info.port === ''){
                    if (console_uri.protocol() == 'http'){
                        new_connection_info.port = '80';
                    }
                    else if (console_uri.protocol() == 'https'){
                        new_connection_info.port = '443';
                    }
                }
                token = console_uri.search(true).token;
                new_connection_info.path = "websockify?token=" + token;
                $scope.novnc_connectioninfo = new_connection_info;
            }else{
                $scope.novnc_connectioninfo = {};
            }
        }, true);

    }]);
