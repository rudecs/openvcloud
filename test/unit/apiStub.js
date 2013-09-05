defineUnitApiStub = function($httpBackend){

	$httpBackend.whenPOST('testapi/users/authenticate').
		respond(function(method, url, data) {
			var credentials = angular.fromJson(data);
			if (credentials.username == 'error'){
				return [403,'Unauthorized'];
			}
			return [200,"yep123456789"];
		});
	

    var openwizzycloudspaces = [ 
    {'id': 0, 'name': 'Main cloudspace', 'description': 'Description'},
    {'id': 1, 'name': 'Production cloudspace', 'description': 'Production Cloudspace'}
    ];

    var openwizzymachines = [{"status": "", "hostname": "", "description": "Webserver", "name": "test", "nics": [], "sizeId": 0, "imageId": 0, "id": 0},
     {"status": "", "hostname": "", "description": "Webserver",  "name": "test2", "nics": [], "sizeId": 0, "imageId": 1, "id": 1}];

    var openwizzyimages = [
             {'id':0, 'name':'Linux', 'description':'An ubuntu 13.04 image', "type": "Windows"},
             {'id':1, 'name':'Windows', 'description': 'A windows 2012 server', "type": "Linux"}
             ];

    var openwizzysizes = [
    {'id':0, 'name':'small', 'CU':1, 'disksize': 20},
    {'id':1, 'name':'medium', 'CU':2, 'disksize': 40},
    {'id':2, 'name':'small', 'CU':4, 'disksize': 100}];


    $httpBackend.whenGET('testapi/machines/get?authkey=null' + '&machineId=' + 0).respond(openwizzymachines[0]);
    $httpBackend.whenGET('testapi/machines/get?authkey=null' + '&machineId=' + 44534).respond(500, 'Not Found');
    $httpBackend.whenGET('testapi/machines/list?authkey=null' + '&cloudspaceId=' + 0 + '&type=').respond(openwizzymachines);
    $httpBackend.whenGET('testapi/sizes/list?authkey=null').respond(openwizzysizes);
    $httpBackend.whenGET('testapi/images/list?authkey=null').respond(openwizzyimages);
    $httpBackend.whenGET('testapi/machines/create?authkey=null&cloudspaceId=0&name=test_create&description=Test Description&sizeId=0&imageId=0').respond(200, 3);

    
};

