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

            getById: function(id) {
                return _.find(this.get(), function(m) { return m.id == id; }); // '==' here is intentional
            },

            save: function(item) {
                var items = this.get();
                for (var i = 0; i < items.length; i++) {
                    if (items[i].id == item.id) {
                        items[i] = item;
                    }
                }
                this.set(items);
            },

            set: function(items) {
                localStorage.setItem(key, JSON.stringify(items));
            },

            add: function(item) {
                var items = this.get() || [];
                items.push(item);
                this.set(items);
            },

            remove: function(id) {
                var items = this.get();
                var index = -1;
                for (var i = 0; i < items.length; i++) {
                    if (items[i].id == id) {
                        index = i;
                        break;
                    }
                }
                if (index == -1)
                    return;
                items.splice(index, 1);
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
            "interfaces": [{'ipAddress': '192.168.100.123'}],
            "sizeId": 0,
            "imageId": 0,
            "id": 0
        }, {
            "status": "HALTED",
            "hostname": "cloudbroker.cloudscalers.com",
            "description": "CloudScalers CloudBroker",
            "name": "CloudBroker",
            "interfaces": [{'ipAddress': '192.168.100.66'}],
            "sizeId": 0,
            "imageId": 1,
            "id": 1
        }]);
    }

    var images = [
        {id: 0, type: 'Ubuntu', name: 'Ubuntu 13.04 x64', description: 'Ubuntu 13.04 x64'},
        {id: 1, type: 'Ubuntu', name: 'Ubuntu 13.04 x32', description: 'Ubuntu 13.04 x32'},
        {id: 2, type: 'Ubuntu', name: 'Ubuntu 12.10 x64', description: 'Ubuntu 12.10 x64'},
        {id: 3, type: 'Ubuntu', name: 'Ubuntu 12.10 x32', description: 'Ubuntu 12.10 x32'},
        {id: 4, type: 'Ubuntu', name: 'Ubuntu 12.04 x64', description: 'Ubuntu 12.04 x64'},
        {id: 5, type: 'Ubuntu', name: 'Ubuntu 12.04 x32', description: 'Ubuntu 12.04 x32'},
        {id: 6, type: 'Ubuntu', name: 'Ubuntu 10.04 x64', description: 'Ubuntu 10.04 x64'},
        {id: 7, type: 'Ubuntu', name: 'Ubuntu 10.04 x32', description: 'Ubuntu 10.04 x32'},
        {id: 8, type: 'CentOS', name: 'CentOS 6.4 x64', description: 'CentOS 6.4 x64'},
        {id: 9, type: 'CentOS', name: 'CentOS 6.4 x32', description: 'CentOS 6.4 x32'},
        {id: 10, type: 'CentOS', name: 'CentOS 5.8 x64', description: 'CentOS 5.8 x64'},
        {id: 11, type: 'CentOS', name: 'CentOS 5.8 x32', description: 'CentOS 5.8 x32'},
        {id: 12, type: 'Debian', name: 'Debian 7.0 x64', description: 'Debian 7.0 x64'},
        {id: 13, type: 'Debian', name: 'Debian 7.0 x32', description: 'Debian 7.0 x32'},
        {id: 14, type: 'Debian', name: 'Debian 6.0 x64', description: 'Debian 6.0 x64'},
        {id: 15, type: 'Debian', name: 'Debian 6.0 x32', description: 'Debian 6.0 x32'},
        {id: 16, type: 'Arch Linux', name: 'Arch Linux 2013.05 x64', description: 'Arch Linux 2013.05 x64'},
        {id: 17, type: 'Arch Linux', name: 'Arch Linux 2013.05 x32', description: 'Arch Linux 2013.05 x32'},
        {id: 18, type: 'Fedora', name: 'Fedora 17 x64', description: 'Fedora 17 x64'},
        {id: 19, type: 'Fedora', name: 'Fedora 17 x32', description: 'Fedora 17 x32'},
    ];

    var sizes = [
        {id: 0, CU: 1, disksize: '512MB', 'name': '512MB Memory, 1 Core, 10GB at SSD Speed, Unlimited Transfer - 5 USD/month'},
        {id: 1, CU: 1, disksize: '1GB', 'name': '1GB Memory, 1 Core, 10GB at SSD Speed, Unlimited Transfer - 8 USD/month'},
        {id: 2, CU: 2, disksize: '2GB', 'name': '2GB Memory, 2 Cores, 10GB at SSD Speed, Unlimited Transfer - 17 USD/month'},
        {id: 3, CU: 2, disksize: '4GB', 'name': '4GB Memory, 2 Cores, 10GB at SSD Speed, Unlimited Transfer - 35 USD/month'},
        {id: 4, CU: 4, disksize: '8GB', 'name': '8GB Memory, 4 Cores, 10GB at SSD Speed, Unlimited Transfer - 73 USD/month'},
        {id: 5, CU: 8, disksize: '16GB', 'name': '16GB Memory, 8 Cores, 10GB at SSD Speed, Unlimited Transfer - 145 USD/month'},
        {id: 6, CU: 12, disksize: '32GB', 'name': '32GB Memory, 12 Cores, 10GB at SSD Speed, Unlimited Transfer - 289 USD/month'},
        {id: 7, CU: 16, disksize: '48GB', 'name': '48GB Memory, 16 Cores, 10GB at SSD Speed, Unlimited Transfer - 433 USD/month'},
        {id: 8, CU: 20, disksize: '64GB', 'name': '64GB Memory, 20 Cores, 10GB at SSD Speed, Unlimited Transfer - 577 USD/month'},
    //        {id: 9, CU: 24, disksize: '96GB', 'name': '96GB Memory, 24 Cores, 10GB at SSD Speed, Unlimited Transfer - 865 USD/month'},
    ];

    var actionlist = {
        'stop': 'HALTED',
        'start': 'RUNNING'
    };


    $httpBackend.whenGET(/^\/machines\/get\?machineId=(.+).*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        if (!_.find(MachinesList.get(), function(m) { return m.id == params.machineId; })) {
            return [500, 'Not found']
        }
        var matchedMachine = MachinesList.getById(params.machineId);
        return [200, matchedMachine];
    });

    $httpBackend.whenGET(/^\/machines\/list\?.*/).respond(function (method, url, data) {
        return [200, _.values(MachinesList.get())];
    });
    $httpBackend.whenGET(/^\/images\/list\?.*/).respond(images);
    $httpBackend.whenGET(/^\/sizes\/list\?.*/).respond(sizes);
    $httpBackend.whenGET(/^\/machines\/create\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var id = Math.random();
        var machine = {
            "status": "RUNNING",
            "cloudspaceId": params.cloudspaceId,
            "hostname": params.name,
            "description": params.description,
            "name": params.name,
            "interfaces": [{'ipAddress':'192.168.100.34'}],
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
    $httpBackend.whenGET(/^\/machines\/action\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var action = params.action;
        var machineid = params.machineId;
        if (!_.has(actionlist, action)) {
            return [500, 'Invallid action'];
        }
        var machine = MachinesList.getById(machineid);
        machine.status = actionlist[action];
        MachinesList.save(machine);
        return [200, true];
    });

    $httpBackend.whenGET(/^\/machines\/delete\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        console.log('Stub Delete ' + machineid);
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        MachinesList.remove(machineid);
        return [200, true];
    });

    // Snapshots
    var snapshots = [
        "snap1",
        "snap2",
        "snap3",
        "snap4"
    ];

    $httpBackend.whenGET(/\/machines\/listSnapshots\?.*/).respond(snapshots);
    
    $httpBackend.whenGET(new RegExp('/machines/snapshot\\?machineId=2&name=.*?\&api_key=(.*?)')).respond(function(status, data) {
        return [500, "Can't create snapshot"];
    });
    $httpBackend.whenGET(/\/machines\/snapshot\?.*/).respond(function(status, data) {
        var params = new URI(url).search(true);
        var name = params.name;
        snapshots.push(name);
        return [200, name];
    });

    

    // getConsoleUrl
    $httpBackend.whenGET(/^\/machines\/getConsoleUrl\?machineId=(\d+).*/).respond('".files/img/console.png"');

    // actions
    $httpBackend.whenGET(/^\/machines\/start\?machineId=\d+.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        var machine = MachinesList.getById(machineid);
        machine.status = 'RUNNING';
        MachinesList.save(machine);
        return [200, 'RUNNING'];
    });

    $httpBackend.whenGET(/^\/machines\/stop\?machineId=\d+.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        var machine = MachinesList.getById(machineid);
        machine.status = 'HALTED';
        MachinesList.save(machine);
        return [200, 'HALTED'];
    });

    $httpBackend.whenGET(/^\/machines\/pause\?machineId=\d+.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        var machine = MachinesList.getById(machineid);
        machine.status = 'PAUSED';
        MachinesList.save(machine);
        return [200, 'PAUSED'];
    });

    $httpBackend.whenGET(/^\/machines\/resume\?machineId=\d+.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        var machine = MachinesList.getById(machineid);
        machine.status = 'RUNNING';
        MachinesList.save(machine);
        return [200, 'RUNNING'];
    });

    $httpBackend.whenGET(/^\/machines\/rename\?machineId=.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var machineid = params.machineId;
        var newName = params.newName;
        var machines = MachinesList.get();
        if (!_.find(machines, function(m) { return m.id == machineid; })) {
            return [500, 'Machine not found'];
        }
        var machine = MachinesList.getById(machineid);
        machine.name = newName;
        MachinesList.save(machine);
        return [200, 'OK'];
    });

    // clone
    $httpBackend.whenGET(/^\/machines\/clone\?machineId=\d+.*/).respond('OK');
};

