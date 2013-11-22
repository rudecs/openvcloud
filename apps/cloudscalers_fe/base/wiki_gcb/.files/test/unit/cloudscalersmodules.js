var cloudscalers = angular.module('cloudscalers',['cloudscalers.SessionServices',
                                                  'cloudscalers.AccountServices',
                                                  'cloudscalers.CloudSpaceServices',
                                                  'cloudscalers.machineServices',
                                                  'cloudscalers.controllers',
                                                  'ngRoute']);

angular.module('cloudscalers.controllers', ['ui.bootstrap', 'ui.slider', 'cloudscalers.machineServices','cloudscalers.AccountServices','cloudscalers.CloudSpaceServices', 'cloudscalers.directives']);


//So we can inject our own functions instead of the builtin functions
cloudscalers.value('confirm', window.confirm);
cloudscalers.value('alert', window.alert);