defineApiStub = function ($httpBackend) {


    $httpBackend.whenGET(/^pages\//).passThrough();

    // Saves items in localStorage, under the given key. This allows us to persist items in the front-end.
    function LocalStorageItem(key) {
        return {
            get: function() {
                var items = localStorage.getItem(key);
                if (items)
                    return JSON.parse(items);
                return undefined;
            },

            getById: function(id) {
                return _.find(this.get(), function(m) { return m.id == id; }); // '==' here is intentional
            },

            getByName: function(machineName) {
                return _.find(this.get(), function(m) { return m.hostname == machineName; });
                console.log(m);
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
        var user = _.findWhere(UsersList.get(), credentials);
        if (!user) {
            return [403, 'Unauthorized'];
        }
        return [200, '"yep123456789"'];
    });

    $httpBackend.whenPOST('/users/register').respond(function(method, url, data) {
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
        	"cloudspaceId":1,
            "status": "RUNNING",
            "hostname": "jenkins.cloudscalers.com",
            "accounts":[{"password":"xGuiyrRp","login":"cloudscalers","guid":""}],
            "description": "JS Webserver",
            "name": "CloudScalers Jenkins",
            "interfaces": [{'ipAddress': '192.168.100.123'}],
            "sizeId": 0,
            "imageId": 0,
            "id": 0
        }, {
        	"cloudspaceId":1,
            "status": "HALTED",
            "hostname": "cloudbroker.cloudscalers.com",
            "accounts":[{"password":"nGGuqMKJrRp","login":"cloudscalers","guid":""}],
            "description": "CloudScalers CloudBroker",
            "name": "CloudBroker",
            "interfaces": [{'ipAddress': '192.168.100.66'}],
            "sizeId": 0,
            "imageId": 1,
            "id": 1
        }]);
    }

    var images = [
        {
            "name": "Windows 2008 Server",
            "UNCPath": "",
            "description": "",
            "type": "Windows",
            "id": 2,
            "size": 50
        },
        {
            "name": "Linux 13.04 image",
            "UNCPath": "",
            "description": "",
            "type": "Ubuntu",
            "id": 1,
            "size": 50
        }
    ];

    var sizes = [
        {
        "vcpus": 4,
        "description": "10GB at SSD Speed, Unlimited Transfer - 70 USD/month",
        "id": 4,
        "name": "",
        "memory": 8192
        },
        {
        "vcpus": 8,
        "description": "10GB at SSD Speed, Unlimited Transfer - 140 USD/month",
        "id": 5,
        "name": "",
        "memory": 16384
        },
        {
        "vcpus": 1,
        "description": "10GB at SSD Speed, Unlimited Transfer - 7.5 USD/month",
        "id": 1,
        "name": "",
        "memory": 512
        },
        {
        "vcpus": 12,
        "description": "10GB at SSD Speed, Unlimited Transfer - 250 USD/month",
        "id": 6,
        "name": "",
        "memory": 32768
        },
        {
        "vcpus": 1,
        "description": "10GB at SSD Speed, Unlimited Transfer - 15 USD/month",
        "id": 2,
        "name": "",
        "memory": 1024
        },
        {
        "vcpus": 16,
        "description": "10GB at SSD Speed, Unlimited Transfer - 350 USD/month",
        "id": 7,
        "name": "",
        "memory": 49152
        },
        {
        "vcpus": 2,
        "description": "10GB at SSD Speed, Unlimited Transfer - 18 USD/month",
        "id": 3,
        "name": "",
        "memory": 2048
        },
        {
        "vcpus": 20,
        "description": "10GB at SSD Speed, Unlimited Transfer - 465 USD/month",
        "id": 8,
        "name": "",
        "memory": 65536
        },
        {
        "vcpus": 2,
        "description": "10GB at SSD Speed, Unlimited Transfer - 36 USD/month",
        "id": 10,
        "name": "",
        "memory": 4096
        }
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

    $httpBackend.whenGET(/^\/machines\/list\?cloudspaceId=(\d+).*/).respond(function (method, url, data) {
    	var params = new URI(url).search(true);
        var cloudspaceId = params.cloudspaceId;
    	return [200, _.values(_.filter(MachinesList.get(), function(machine){
    		return machine.cloudspaceId == cloudspaceId;
    	}))];
    });
    $httpBackend.whenGET(/^\/images\/list\b.*/).respond(images);
    $httpBackend.whenGET(/^\/sizes\/list\b.*/).respond(sizes);
    $httpBackend.whenGET(/^\/machines\/create\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        if(MachinesList.getByName(params.name) == undefined){
            var id = Math.random();
            var machine = {
                status: "RUNNING",
                cloudspaceId: parseInt(params.cloudspaceId),
                hostname: params.name,
                description: params.description,
                name: params.name,
                accounts:[{password:"xGiooOyrRp",login:"cloudscalers",guid:""}],
                interfaces: [{'ipAddress':'192.168.100.34'}],
                sizeId: parseInt(params.sizeId),
                imageId: parseInt(params.imageId),
                disksize: parseInt(params.disksize),
                archive: params.archive,
                region: params.region,
                replication: params.replication,
                id: id
            };
                MachinesList.add(machine);
                return [200, id];
        }
        else{
            return [409, 'Machine name duplicated!']
        }
    });

    $httpBackend.whenGET(/^\/machines\/update\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var machine = MachinesList.getById(params.machineId);
        machine.description = params.description;
        MachinesList.save(machine);
        return [200, true];
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

    $httpBackend.whenGET(new RegExp('/machines/snapshot\\?machineId=2&name=.*?(&api_key=.*?)')).respond(function(status, data) {
        return [500, "Can't create snapshot"];
    });
    $httpBackend.whenGET(/\/machines\/snapshot\?.*/).respond(function(status, data) {
        var params = new URI(url).search(true);
        var name = params.name;
        snapshots.push(name);
        return [200, name];
    });



    // getConsoleUrl
    $httpBackend.whenGET(/^\/machines\/getConsoleUrl\?machineId=(\d+).*/).respond('null');


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

    $httpBackend.whenGET(/^\/accounts\/list.*/).respond([
        {id: '1', name: 'Lenny Miller'},
        {id: '2', name: 'Awingu'},
        {id: '4', name: 'Incubaid'},
    ]);
    var cloudspaces = [
       {id: '1', name: 'Default', accountId: '1'},
       {id: '2', name: 'Development', accountId: '2'},
       {id: '3', name: 'Training', accountId: '2'},
       {id: '4', name: 'Production', accountId: '2'},
       {id: '5', name: 'Development', accountId: '4'},
       {id: '6', name: 'Acceptance', accountId: '4'},
       {id: '7', name: 'Production', accountId: '4'},
    ];

    var cloudSpace = {
        name: 'Development',
        descr: 'Development machine',
        acl: [{
                "type": "U",
                "guid": "",
                "right": "CXDRAU",
                "userGroupId": "user 1"
            }, {
                "type": "U",
                "guid": "",
                "right": "CXDRAU",
                "userGroupId": "user 2"
            }
        ]
    };

    $httpBackend.whenGET(/^\/cloudspaces\/list.*/).respond(cloudspaces);
    $httpBackend.whenGET(/^\/cloudspaces\/get\?.*/).respond(cloudSpace);

    $httpBackend.whenGET(/^\/cloudspaces\/addUser\?.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var userId = params.userId.toLowerCase();
        if (userId.indexOf('user') >= 0) {
            cloudSpace.acl.push({ type: 'U', guid: '', right: 'CXDRAU', userGroupId: userId});
            return [200, "Success"];
        } else if (userId.indexOf('not found') >= 0) {
            return [404, 'User not found'];
        } else if (userId.indexOf('eee') >= 0) {
            return [3000, 'Unspecified error'];
        } else {
            return [500, 'Server error'];
        }
    });
    $httpBackend.whenGET(/^\/cloudspaces\/deleteUser\?.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var userId = params.userId;
        cloudSpace.acl = _.reject(cloudSpace.acl, function(acl) { return acl.userGroupId == userId});
        return [200, 'Success'];
    });

    $httpBackend.whenGET(/^\/cloudspaces\/create.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        if (_.findWhere(cloudspaces, {name: params.name}))
            return [500, 'Cloudspace already exists'];

        cloudspaces.push({
            id: '15',
            name: params.name,
            accountId: params.accountId,
            acl: [
                {
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "linny"
                }, {
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "harvey"
                }
            ],
        });
        return [200, '15']; // ID = 15
    });

    $httpBackend.whenGET(/^\/cloudspaces\/delete\?.*/).respond(function (method, url, data) {
        var params = new URI(url).search(true);
        var cloudSpaceItem = _.where(cloudspaces, {id: params.cloudspaceId, accountId: params.userId});
        if(cloudSpaceItem.length > 0){
            cloudspaces.splice(_.where(cloudspaces, {id: params.cloudspaceId, accountId: params.userId}), 1);
            return [200, true];
        }else{
            return [500, "Cloudspace couldn't found!"];
        }
    });

    var account = {
        name: 'Linny Miller',
        descr: 'Mr. Linny Miller',
        acl: [{
                "type": "U",
                "guid": "",
                "right": "CXDRAU",
                "userGroupId": "linny"
            }, {
                "type": "U",
                "guid": "",
                "right": "CXDRAU",
                "userGroupId": "harvey"
            }
        ]
    };
    $httpBackend.whenGET(/^\/accounts\/get\?.*/).respond(account);


    $httpBackend.whenGET(/^\/accounts\/addUser\?.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var userId = params.userId.toLowerCase();
        if (userId.indexOf('user') >= 0) {
            account.acl.push({ type: 'U', guid: '', right: 'CXDRAU', userGroupId: userId});
            return [200, "Success"];
        } else if (userId.indexOf('not found') >= 0) {
            return [404, 'User not found'];
        } else if (userId.indexOf('eee') >= 0) {
            return [3000, 'Unspecified error'];
        } else {
            return [500, 'Server error'];
        }
    });
    $httpBackend.whenGET(/^\/accounts\/deleteUser\?.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        var userId = params.userId;
        account.acl = _.reject(account.acl, function(acl) { return acl.userGroupId == userId});
        return [200, 'Success'];
    });


    $httpBackend.whenGET(/^\/machines\/getHistory\?.*/).respond([
        {
            _source: {
                message: "stop",
                epoch: 1389016668
            }
        },
        {
            _source: {
                message: "start",
                epoch: 1389015668
            }
        },
    ]);

    $httpBackend.whenGET(/^\/users\/get\?.*/).respond({
        username: 'tayseer_test',
        emailaddresses: [ 'tayseer_test123@site.com' ]
    });

    $httpBackend.whenGET(/^\/accounts\/getCreditBalance.*/).respond("20");

    $httpBackend.whenGET(/^\/accounts\/getCreditHistory.*/).respond([
       {
            status: "PROCESSED",
            currency: "LTC",
            amount: 0.43383948,
            reference: "e50d4d6866279ebc18bbe2ef84d187b050b9ed998340c1ef5f74b2d565c7d550",
            time: 1391516164,
            credit: 10.000000014000001,
            comment: "Credit",
            accountid: "fe8409b1-fa21-4fc1-b2d3-c752928c450c"
        },
        {
            status: "PROCESSED",
            currency: "LTC",
            amount: 0.43383948,
            reference: "a33f6a65550a7512c0c56c55a0057023a9a987233bd4eb692a9c1c2e788957dd",
            time: 1391432480,
            credit: 10.000000014000001,
            comment: "Credit",
            accountid: "fe8409b1-fa21-4fc1-b2d3-c752928c450c"
        }
    ]);

    $httpBackend.whenGET(/^\/payments\/getPaymentInfo.*/).respond(function(method,url,data)
    {
        var params = new URI(url).search(true);
        var coin = params.coin;
        if (coin == 'BTC') {
            return [200,{coin: "BTC", value: 800.05, address: "1BBnbfhkkVVAan61362PkhGMdjXk5YsrmP"}];
        } else if (coin == 'LTC') {
            return [200,{coin: "LTC", value: 23.05, address: "LZLRqxWip27u5pGzc1amMhcaH16VRMSaYt"}];
        } else  {
            return [504, 'Bad request'];
        }

    });

    var storages = [
       {url: "https://mybucketname.uss3.vscalers.com", accesskey:"ALSECKCKDKMKC5GUSNFA", size: 1984995885, cloudspaceId: 1},
       {url: "https://mybucketname.uss3.vscalers.com", accesskey:"bbbbbbbbbbbbbbbbbbbb", size: 2984995885, cloudspaceId: 1},
    ];
    $httpBackend.whenGET(/^\/storagebuckets\/list\?cloudspaceId=\d+.*/).respond(storages);

    var portforwarding = [
       {id: 1,ip: '125.85.7.1', vmName: 'CloudScalers Jenkins', puplicPort: 8080, localPort: 80},
       {id: 2,ip: '125.85.7.1', vmName: 'CloudScalers Jenkins', puplicPort: 2020, localPort: 20},
       {id: 3,ip: '125.85.7.1', vmName: 'CloudScalers Jenkins', puplicPort: 7070, localPort: 70},
       {id: 4,ip: '125.85.7.1', vmName: 'CloudBroker', puplicPort: 9090, localPort: 90},
       {id: 5,ip: '125.85.7.1', vmName: 'CloudBroker', puplicPort: 3030, localPort: 30},
       {id: 6,ip: '125.85.7.1', vmName: 'CloudBroker', puplicPort: 8080, localPort: 80},
       {id: 7,ip: '126.84.3.9', vmName: 'CloudScalers Jenkins', puplicPort: 2020, localPort: 20},
       {id: 8,ip: '126.84.3.9', vmName: 'CloudScalers Jenkins', puplicPort: 4040, localPort: 40},
       {id: 9,ip: '126.84.3.9', vmName: 'CloudScalers Jenkins', puplicPort: 6060, localPort: 60},
       {id: 10,ip: '126.84.3.9', vmName: 'CloudBroker', puplicPort: 1010, localPort: 10},
       {id: 11,ip: '126.84.3.9', vmName: 'CloudBroker', puplicPort: 3030, localPort: 30},
       {id: 12,ip: '126.84.3.9', vmName: 'CloudBroker', puplicPort: 5050, localPort: 50},
    ];
    $httpBackend.whenGET(/^\/portforwarding\/list.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        if(params.id == undefined){
            return [200, portforwarding];
        }else{
            var filteredPorts = _.where(portforwarding, {id: parseInt(params.id)});
            return[200, filteredPorts];
        }
    });
    $httpBackend.whenGET(/^\/portforwarding\/list\?id=\d+.*/).respond(storages);

    $httpBackend.whenGET(/^\/commonports\/list.*/).respond([
        {port: '80', name: 'HTTP'},
        {port: '72', name: 'SSH'},
        {port: '403', name: 'HTTPS'},
        {port: '27', name: 'FTP'}
    ]);

    $httpBackend.whenGET(/^\/portforwarding\/create.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        portforwarding.push({
            ip: params.ip,
            vmName: params.vmName,
            puplicPort: params.puplicPort,
            localPort: params.localPort
        });
        return [200, params.ip];
    });

    $httpBackend.whenGET(/^\/portforwarding\/update.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        for (var i = 0, l = portforwarding.length; i < l; i++) {
            if (portforwarding[i].id === parseInt(params.id)) {
                portforwarding[i].ip = params.ip;
                portforwarding[i].puplicPort = params.puplicPort;
                portforwarding[i].vmName = params.vmName;
                portforwarding[i].localPort = params.localPort;
                break;
            }
        }
        return [200, portforwarding];
    });

    $httpBackend.whenGET(/^\/portforwarding\/delete.*/).respond(function(method, url, data) {
        var params = new URI(url).search(true);
        portforwarding.splice(_.where(portforwarding, {id: parseInt(params.id)}) , 1)
        return [200, portforwarding];
    });
};
