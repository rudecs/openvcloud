describe('CloudSpaceServices', function() {
    var $httpBackend, Account;

    beforeEach(module('cloudscalers.services'));

    beforeEach(inject(function(_$httpBackend_, _CloudSpace_) {
        $httpBackend = _$httpBackend_;
        CloudSpace = _CloudSpace_;
        defineUnitApiStub($httpBackend);
    }));

    it('can list all CloudSpaces', function() {
        var CloudSpaceList;
        CloudSpace.list().then(function(result) {
            CloudSpaceList = result;
        });
    
        expect(CloudSpaceList).toBeUndefined();
        $httpBackend.flush();
        expect(CloudSpaceList).toBeDefined();
        expect(CloudSpaceList.length).toBe(8);
        expect(CloudSpaceList[2]).toEqual({id: '3', name: 'Cloudspace 3', accountId: '2'});
    });

    // TODO: This will be changed when I 
    it('can add user', function() {
        var addUserResult;
        CloudSpace.addUser({cloudSpaceId: 1}, {id: 10}, {'R': true}).then(function(result) {
            addUserResult = result;
        });
        expect(addUserResult).toBeUndefined();
        $httpBackend.flush();
        expect(addUserResult).toEqual("Success");
    });

    it('can handle user addition failure', function() {
        var addUserResult;
        CloudSpace.addUser({cloudSpaceId: 1}, {id: 20}, {'R': true}).then(function(result) {
            addUserResult = result;
        });
        expect(addUserResult).toBeUndefined();
        $httpBackend.flush();
        expect(addUserResult).toEqual("Failed");
    });

    it('can delete user', function() {
        var deleteUserResult;
        CloudSpace.deleteUser({cloudSpaceId: 1}, {id: 10}).then(function(result) {
            deleteUserResult = result;
        });
        expect(deleteUserResult).toBeUndefined();
        $httpBackend.flush();
        expect(deleteUserResult).toEqual("Success");
    });

    it('can handle user deletion failure', function() {
        var deleteUserResult;
        CloudSpace.deleteUser({cloudSpaceId: 1}, {id: 20}).then(function(result) {
            deleteUserResult = result;
        });
        expect(deleteUserResult).toBeUndefined();
        $httpBackend.flush();
        expect(deleteUserResult).toEqual("Failed");
    });

});