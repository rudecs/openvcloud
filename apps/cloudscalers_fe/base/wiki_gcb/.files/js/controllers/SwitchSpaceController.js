angular.module('cloudscalers.controllers')
    .controller('SwitchSpaceController', ['$scope','$window', 'SessionData', 'CloudSpace', function($scope, $window, SessionData, CloudSpace) {

        var uri = new URI($window.location);
        queryparams = URI.parseQuery(uri.query());
        api_key = queryparams.token;
        username = queryparams.username;
        spaceId = queryparams.space;

        SessionData.setUser({username: username, api_key: api_key});
        CloudSpace.setCurrent({id:spaceId});

        var uri = new URI($window.location);
        uri.filename('Decks');
        uri.fragment('');
        uri.search('');
        $window.location = uri.toString();

    }]);
