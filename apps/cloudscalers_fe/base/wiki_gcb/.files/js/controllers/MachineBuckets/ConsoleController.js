
cloudscalersControllers
    .controller('ConsoleController', ['$scope','$routeParams', 'Machine', function($scope, $routeParams, Machine) {
        $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
        $scope.novnc_connectioninfo = {}
        
        $scope.$watch('$parent.machine.status', function(newvalue, oldvalue) {
            if (newvalue == 'RUNNING')
                $scope.machineConsoleUrlResult = Machine.getConsoleUrl($routeParams.machineId);
        }, true);
        
        $scope.$watch('machineConsoleUrlResult',function(newvalue, oldvalue){
        	if (newvalue.url){
        		var new_connection_info = {};
        		console_uri = URI(newvalue.url);
        		new_connection_info.host = console_uri.hostname();
        		new_connection_info.port = console_uri.port();
        		
        		
        		if (new_connection_info.port == ''){
        			if (console_uri.protocol() == 'http'){
        				new_connection_info.port = '80';
        			}
        			else if (console_uri.protocol() == 'https'){
        				new_connection_info.port = '443';
        			};
        		};
        		
        		
        		
            	token = console_uri.search(true)['token']
            	new_connection_info.path = "websockify?token=" + token;
            	
            	$scope.novnc_connectioninfo = new_connection_info;
        	}
        	
        }, true);
        
    }]);
