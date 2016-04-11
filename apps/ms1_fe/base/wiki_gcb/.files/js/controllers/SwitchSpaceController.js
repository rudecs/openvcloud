(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('SwitchSpaceController', SwitchSpaceController);
  function SwitchSpaceController($scope, $window, SessionData, CloudSpace) {
    var uri = new URI($window.location);
    var queryparams = URI.parseQuery(uri.query());
    var apiKey = queryparams.token;
    var username = queryparams.username;
    var spaceId = queryparams.spaceId;

    SessionData.setUser({username: username, api_key: apiKey});
    CloudSpace.setCurrent({id: spaceId});
    //FIX: uri is already defined and assigned with this value before
    uri = new URI($window.location);
    uri.filename('Decks');
    uri.fragment('');
    uri.search('');
    $window.location = uri.toString();
  }

})();
