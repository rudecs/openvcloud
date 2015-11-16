angular.module('cloudscalers.controllers')
    .controller('SwitchSpaceController', ['$scope','$window', 'SessionData', 'CloudSpace', function($scope, $window, SessionData, CloudSpace) {

        var uri = new URI($window.location);
        var queryparams = URI.parseQuery(uri.query());
        var api_key = queryparams.token;
        var username = queryparams.username;
        var spaceId = queryparams.spaceId;
        console.log(queryparams);

        SessionData.setUser({username: username, api_key: api_key});
        CloudSpace.setCurrent({id:spaceId});

        var uri = new URI($window.location);
        uri.filename('Decks');
        uri.fragment('');
        uri.search('');
        $window.location = uri.toString();

    }]);
