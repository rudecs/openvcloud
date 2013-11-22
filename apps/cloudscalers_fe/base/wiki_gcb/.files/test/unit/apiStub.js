defineUnitApiStub = function($httpBackend){

	$httpBackend.whenPOST('testapi/users/authenticate').
		respond(function(method, url, data) {
			var credentials = angular.fromJson(data);
			if (credentials.username == 'error'){
				return [403,'Unauthorized'];
			}
			return [200,'"yep123456789"'];
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


    $httpBackend.whenGET(/^testapi\/machines\/list\?cloudspaceId=0&type=(&authke.*)?$/).respond(openwizzymachines);
    
    $httpBackend.whenGET(/^testapi\/machines\/get\?machineId=0(&authke.*)?/).respond(openwizzymachines[0]);
    $httpBackend.whenGET(/^testapi\/images\/list.*/).respond(openwizzyimages);

    $httpBackend.whenGET(/^testapi\/sizes\/list(\?.*)?/).respond(openwizzysizes);
    
    
    $httpBackend.whenGET(/^testapi\/machines\/delete\?machineId=7.*/).respond(function() { return [200, 'success']; });
    $httpBackend.whenGET(/^testapi\/machines\/delete\?machineId=2(&authke.*)?/).respond(function() { return [500, 'error']; });

    // getConsoleUrl
    $httpBackend.whenGET(/^testapi\/machines\/getConsoleUrl\?machineId=13(&authke.*)?/).respond('"http://www.reddit.com/"');
    $httpBackend.whenGET(/^testapi\/machines\/getConsoleUrl\?machineId=3(&authke.*)?/).respond('None');

    // Snapshots
    var snapshots = [
        "snap1",
        "snap2",
        "snap3",
        "snap4"
    ];

    $httpBackend.whenGET(/^testapi\/machines\/listSnapshots\?machineId=7.*/).respond(snapshots);
    $httpBackend.whenGET(/^testapi\/machines\/listSnapshots\?machineId=2.*/).respond(snapshots);
    var urlRegexpForSuccess = /^testapi\/machines\/snapshot\?machineId=7\&name=(.*?)&?.*/;
    $httpBackend.whenGET(urlRegexpForSuccess).respond(function(status, data) {
        var name = urlRegexpForSuccess.exec(data)[1];
        snapshots.push(name);
        return [200, name];
    });

    $httpBackend.whenGET(new RegExp('testapi/machines/snapshot\\?machineId=2&name=.*?&?')).respond(function(status, data) {
        return [500, "Can't create snapshot"];
    });

    
};

