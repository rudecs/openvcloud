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

    $httpBackend.whenGET(/^testapi\/accounts\/list.*/).respond([
        {id: '1', name: 'Account 1'},
        {id: '2', name: 'Account 2'},
        {id: '4', name: 'Account 4'},
    ]);

    $httpBackend.whenGET(/^testapi\/cloudspaces\/list\b.*/).respond([
       {id: '1', name: 'Cloudspace 1', accountId: '1'},
       {id: '2', name: 'Cloudspace 2', accountId: '1'},
       {id: '3', name: 'Cloudspace 3', accountId: '2'},
       {id: '4', name: 'Cloudspace 4', accountId: '2'},
       {id: '4', name: 'Cloudspace 5', accountId: '2'},
       {id: '4', name: 'Cloudspace 6', accountId: '4'},
       {id: '4', name: 'Cloudspace 7', accountId: '4'},
       {id: '4', name: 'Cloudspace 8', accountId: '4'},
   ]);

    $httpBackend.whenGET(/^\/accounts\/listUsers.*/).respond([
        {id: 1, name: 'User 1', email: 'user1@mysite.com'},
        {id: 2, name: 'User 2', email: 'user2@mysite.com'},
        {id: 3, name: 'User 3', email: 'arvid@mysite.com'},
        {id: 4, name: 'User 4', email: 'marco@mysite.com'},
        {id: 5, name: 'User 5', email: 'user5@mysite.com'},
        {id: 6, name: 'User 6', email: 'user6@mysite.com'},
    ]);

    $httpBackend.whenGET(/^testapi\/cloudspaces\/listUsers\?.*/).respond([
        {id: 1, name: 'User 1', email: 'user1@mysite.com', access: 'RXC'},
        {id: 2, name: 'User 2', email: 'user2@mysite.com', access: 'RXC'}
    ]);

    $httpBackend.whenGET(/^testapi\/cloudspaces\/addUser\?cloudspaceId=1&accesstype=R&userId=user 10/).respond(200, "Success");
    $httpBackend.whenGET(/^testapi\/cloudspaces\/addUser\?cloudspaceId=1&accesstype=R&userId=user 20/).respond(500, "Failed");
    $httpBackend.whenGET(/^testapi\/cloudspaces\/deleteUser\?cloudspaceId=1&userId=user 10/).respond(200, "Success");
    $httpBackend.whenGET(/^testapi\/cloudspaces\/deleteUser\?cloudspaceId=1&userId=user 20/).respond(500, "Failed");
};

