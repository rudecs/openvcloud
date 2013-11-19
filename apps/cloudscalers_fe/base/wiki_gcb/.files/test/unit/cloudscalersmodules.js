var cloudscalers = angular.module('cloudscalers',['cloudscalers.SessionServices',
                               'cloudscalers.machineServices',
                               'cloudscalers.controllers',
                               'ngRoute']);

angular.module('cloudscalers.controllers', ['ui.bootstrap', 'ui.slider', 'cloudscalers.machineServices', 'cloudscalers.directives']);


//So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.value('alert', window.alert);