angular.module('machineServices', ['ng'])
.factory('User', function($http){
	var user = {};
	user.login = function(username, password){
		var loginResult = {username:username};	
		$http({method: 'POST', data: {username:username, password:password},url: cloudspaceconfig.apibaseurl + '/users/authenticate'}).
		  success(function(data, status, headers, config) {
		    loginResult.authKey = data;
		  }).
		  error(function(data, status, headers, config) {
		    loginResult.error = status;
		  });
		return loginResult;
	};
	return user;
})
.factory('Machine', function($http, $window){
  var authkey = $window.sessionStorage.getItem('user.authKey')
  return {
    action: function(machineid, action){
            var result = []
            url = cloudspaceconfig.apibaseurl + '/machines/action?authkey=' + authkey + '&machineId=' + machineid + '&action=' + action;
            $http.get(url).success(function(data, status, headers, config){
            result.success = true;}).error(function(data, status, headers, config){result.error = status;});
            return result
    },
    create: function(cloudspaceid, name, description, sizeId, imageId){
            var machine = [];
            url = cloudspaceconfig.apibaseurl + '/machines/create?authkey=' + authkey + '&cloudspaceId=' + cloudspaceid + '&name=' + name + '&description=' + description + '&sizeId=' + sizeId + '&imageId=' + imageId;
            $http.get(url).success(
                    function(data, status, headers, config){
                         machine.id = data;
                    }).error(
                            function(data, status, headers, config){
                                    machine.error = status;
                            }
                            );
                return machine;
          },
    delete: function(machineid){
            var result = []
            url = cloudspaceconfig.apibaseurl + '/machines/delete?authkey='+authkey+'&machineId=' + machineid;
            $http.get(url).success(
                            function(data, status, headers, config){
                                    result.success = true;}).error(function(data, status, heades, config){result.error = status;});
            return result;
    },
    list: function(cloudspaceid){
      var machines = [];
      url = cloudspaceconfig.apibaseurl + '/machines/list?authkey='+authkey+'&cloudspaceId=' + cloudspaceid + '&type=';
      $http.get(url).success(
        function(data, status, headers, config){
          _.each(data, function(machine){machines.push(machine);});
        }).error(
        function(data, status, headers, config) {
          machines.error = status;
        });
      return machines;
    },
    get: function(machineid){
      var machine = {id:machineid};
      url = cloudspaceconfig.apibaseurl + '/machines/get?authkey=' + authkey + '&machineId='+ machineid;
      $http.get(url).success(
        function(data, status, headers, config){
          angular.copy(data, machine);
        }).error(
        function(data, status, headers, config){
          machine.error = status;
        });
      return machine;
    }
  }
})
.factory('Image', function($http, $window){
  var authkey = $window.sessionStorage.getItem('user.authKey')
  return{
    list: function(){
      var images = [];
      url = cloudspaceconfig.apibaseurl + '/images/list?authkey=' + authkey;
      $http.get(url).success(
        function(data, status, headers, config){
          _.each(data, function(img){images.push(img);});
        }).error(
        function(data, status, headers, config){
          images.error = status;
        });
      return images;
    }
  }
})
.factory('Size', function($http, $window){
  var authkey = $window.sessionStorage.getItem('user.authKey')
  return{
    list: function(){
      var sizes = [];
      url = cloudspaceconfig.apibaseurl + '/sizes/list?authkey=' + authkey;
      $http.get(url).success(
        function(data, status, headers, config){
          _.each(data, function(size){sizes.push(size);});
        }).error(
        function(data, status, headers, config){
          sizes.error = status;
        });
      return sizes;
    }
  }
});

