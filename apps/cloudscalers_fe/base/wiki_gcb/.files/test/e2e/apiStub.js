defineApiStub = function ($httpBackend) {


    $httpBackend.whenGET(/^partials\//).passThrough();

    // Saves items in localStorage, under the given key. This allows us to persist items in the front-end.
    function LocalStorageItem(key) {
        return {
            get: function() {
                var items = localStorage.getItem(key)
                if (items)
                    return JSON.parse(items);
                return undefined;
            },
            
            set: function(items) {
                localStorage.setItem(key, JSON.stringify(items));
            },

            add: function(item) {
                var items = this.get();
                items.push(item);
                this.set(items);
            }
        };
    }

    var UsersList = LocalStorageItem('gcb:users');

    $httpBackend.whenPOST('/users/authenticate').
    respond(function (method, url, data) {
        var credentials = angular.fromJson(data);
        if (!_.findWhere(UsersList.get(), credentials)) {
            return [403, 'Unauthorized'];
        }
        return [200, "yep123456789"];
    });

    $httpBackend.whenPOST('/users/signup').respond(function(method, url, data) {
        var credentials = angular.fromJson(data);
        var users = UsersList.get();
        if (_.findWhere(users, credentials)) {
            return [441, 'This user is already registered'];
        }
        UsersList.add(credentials);
        return [200, "Success"];
    });

    var cloudspaces = [{
        'id': 0,
        'name': 'Main cloudspace',
        'description': 'Description'
    }, {
        'id': 1,
        'name': 'Production cloudspace',
        'description': 'Production Cloudspace'
    }];

    var MachinesList = LocalStorageItem('gcb:machines');
    if (!MachinesList.get()) {
        MachinesList.set([{
            "status": "RUNNING",
            "hostname": "jenkins.cloudscalers.com",
            "description": "JS Webserver",
            "name": "CloudScalers Jenkins",
            "nics": [],
            "sizeId": 0,
            "imageId": 0,
            "id": 0
        }, {
            "status": "HALTED",
            "hostname": "cloudbroker.cloudscalers.com",
            "description": "CloudScalers CloudBroker",
            "name": "CloudBroker",
            "nics": [],
            "sizeId": 0,
            "imageId": 1,
            "id": 1
        }]);
    }

    var images = [{
        'id': 0,
        'name': 'Linux',
        'description': 'An ubuntu 13.04 image',
        "type": "Ubuntu"
    }, {
        'id': 1,
        'name': 'Windows',
        'description': 'A windows 2012 server',
        "type": "Windows"
    }];

    var sizes = [
        {id: 0, CU: 1, disksize: '512MB', 'name': '512MB Memory, 1 Core, 10GB at SSD Speed, Unlimited Transfer - 2.5 USD/month'},
        {id: 1, CU: 1, disksize: '1GB', 'name': '1GB Memory, 1 Core, 20GB at SSD Speed, Unlimited Transfer - 8.5 USD/month'},
        {id: 2, CU: 2, disksize: '2GB', 'name': '2GB Memory, 2 Cores, 20GB at SSD Speed, Unlimited Transfer - 17 USD/month'},
        {id: 3, CU: 2, disksize: '4GB', 'name': '4GB Memory, 2 Cores, 20GB at SSD Speed, Unlimited Transfer - 34 USD/month'},
        {id: 4, CU: 4, disksize: '8GB', 'name': '8GB Memory, 4 Cores, 20GB at SSD Speed, Unlimited Transfer - 71 USD/month'},
        {id: 5, CU: 8, disksize: '16GB', 'name': '16GB Memory, 8 Cores, 20GB at SSD Speed, Unlimited Transfer - 139 USD/month'},
        {id: 6, CU: 12, disksize: '32GB', 'name': '32GB Memory, 12 Cores, 20GB at SSD Speed, Unlimited Transfer - 275 USD/month'},
        {id: 7, CU: 16, disksize: '48GB', 'name': '48GB Memory, 16 Cores, 20GB at SSD Speed, Unlimited Transfer - 411 USD/month'},
        {id: 8, CU: 20, disksize: '64GB', 'name': '64GB Memory, 20 Cores, 20GB at SSD Speed, Unlimited Transfer - 547 USD/month'},
        {id: 9, CU: 24, disksize: '96GB', 'name': '96GB Memory, 24 Cores, 20GB at SSD Speed, Unlimited Transfer - 819 USD/month'},
    ];

    var actionlist = {
        'stop': 'HALTED',
        'start': 'RUNNING'
    };


    $httpBackend.whenGET(/^\/machines\/get\?format=jsonraw&machineId=(.+)&api_key=yep123456789/).respond(function (method, url, data) {
        var matches = /^\/machines\/get\?format=jsonraw&machineId=(.+)&api_key=yep123456789/.exec(url);
        var requestedId = matches[1];
        if (!_.has(MachinesList.get(), requestedId)) {
            return [500, 'Not found']
        }
        var matchedMachine = MachinesList.get()[requestedId];
        return [200, matchedMachine];
    });

    $httpBackend.whenGET('/machines/list?format=jsonraw&cloudspaceId=' + 0 + '&type=&api_key=yep123456789').respond(function (method, url, data) {
        return [200, _.values(MachinesList.get())];
    });
    $httpBackend.whenGET(/^\/images\/list?.*/).respond(images);
    $httpBackend.whenGET(/^\/sizes\/list?.*/).respond(sizes);
    $httpBackend.whenGET(/^\/machines\/create\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var id = _.keys(MachinesList.get()).length;
        var machine = {
            "status": "RUNNING",
            "cloudspaceId": params.cloudspaceId,
            "hostname": params.name,
            "description": params.description,
            "name": params.name,
            "nics": [],
            "sizeId": params.sizeId,
            "imageId": params.imageId,
            disksize: params.disksize,
            archive: params.archive,
            region: params.region,
            replication: params.replication,
            "id": id
        };
        MachinesList.add(machine);
        return [200, id];
    });
    $httpBackend.whenGET(/^\/machines\/action\?format=jsonraw&api_key\=yep123456789/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var action = params.action;
        var machineid = params.machineId;
        if (!_.has(actionlist, action)) {
            return [500, 'Invallid action'];
        }
        var machines = MachinesList.get();
        machines[machineid].status = actionlist[action];
        MachinesList.set(machines);
        return [200, true];
    });

    $httpBackend.whenGET(/^\/machines\/delete\?format=jsonraw&authkey\=yep123456789/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        console.log('Stub Delete');
        console.log(machineid);
        var machines = MachinesList.get();
        if (!_.has(machines, machineid)) {
            return [500, 'Machine not found'];
        }
        delete machines[machineid];
        MachinesList.set(machines);
        return [200, true];
    });

    // Snapshots
    var snapshots = [
        "snap1",
        "snap2",
        "snap3",
        "snap4"
    ];

    $httpBackend.whenGET(new RegExp('\/machines\/listSnapshots\\?format=jsonraw&machineId=(\\d+)\&api_key=(.*?)')).respond(snapshots);
    
    var urlRegexpForSuccess = new RegExp('\/machines\/snapshot\\?format=jsonraw&machineId\=\\d+\&snapshotName\=(.*?)\&api_key\=(.*?)$');
    $httpBackend.whenGET(urlRegexpForSuccess).respond(function(status, data) {
        var params = new URI(url).search(true);
        var snapshotName = params.snapshotName;
        snapshots.push(snapshotName);
        return [200, snapshotName];
    });

    $httpBackend.whenGET(new RegExp('/machines/snapshot\\?format=jsonraw&machineId=2&snapshotName=.*?\&api_key=(.*?)')).respond(function(status, data) {
        return [500, "Can't create snapshot"];
    });

    // getConsoleUrl
    $httpBackend.whenGET('/machines/getConsoleUrl?format=jsonraw&machineId=0&api_key=yep123456789').respond('http://www.reddit.com');
    $httpBackend.whenGET('/machines/getConsoleUrl?format=jsonraw&machineId=1&api_key=yep123456789').respond('None');
    $httpBackend.whenGET('/machines/getConsoleUrl?format=jsonraw&machineId=\d+&api_key=yep123456789').respond('http://yahoo.com');

    // actions
    $httpBackend.whenGET(/^\/machines\/boot\?format=jsonraw&machineId=\d+&api_key\=yep123456789/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.has(machines, machineid)) {
            return [500, 'Machine not found'];
        }
        machines[machineid].status = 'RUNNING';
        MachinesList.set(machines);
        return [200, 'RUNNING'];
    });

    $httpBackend.whenGET(/^\/machines\/poweroff\?format=jsonraw&machineId=\d+&api_key\=yep123456789/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.has(machines, machineid)) {
            return [500, 'Machine not found'];
        }
        machines[machineid].status = 'HALTED';
        MachinesList.set(machines);
        return [200, 'HALTED'];
    });

    $httpBackend.whenGET(/^\/machines\/pause\?format=jsonraw&machineId=\d+&api_key\=yep123456789/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.has(machines, machineid)) {
            return [500, 'Machine not found'];
        }
        machines[machineid].status = 'PAUSED';
        MachinesList.set(machines);
        return [200, 'PAUSED'];
    });

    // clone
    $httpBackend.whenGET(/^\/machines\/clone\?format=jsonraw&machineId=\d+&api_key\=yep123456789/).respond('OK');
};
