describe("AccountAccessManagementController tests", function(){
    var $scope, ctrl, $q, $window = {}, $httpBackend, CloudSpace, Account, listUsersDefer, listAccountUsersDefer;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
    	$httpBackend = _$httpBackend_;
        $controller = _$controller_;
		defineUnitApiStub($httpBackend);
		
        $q = _$q_;
        listUsersDefer = $q.defer();
        listAccountUsersDefer = $q.defer();
        CloudSpace = {
            listUsers: jasmine.createSpy('listUsers').andReturn(listUsersDefer.promise),
            addUser: jasmine.createSpy('addUser')
        };
        Account = {
            listUsers: jasmine.createSpy('listUsers').andReturn(listAccountUsersDefer.promise),
        };

        $scope = $rootScope.$new();
        $scope.currentSpace = {
            cloudSpaceId: 15
        }
        ctrl = $controller('AccountAccessManagementController', {
            $scope: $scope,
            CloudSpace: CloudSpace,
            Account: Account
        });

        listUsersDefer.resolve([
            {id: 1, name: 'User 1', email: 'user1@mysite.com', access: 'RXC'},
            {id: 2, name: 'User 2', email: 'user2@mysite.com', access: 'RXC'}
        ]);
        listAccountUsersDefer.resolve([
            {id: 1, name: 'User 1', email: 'user1@mysite.com'},
            {id: 2, name: 'User 2', email: 'user2@mysite.com'},
            {id: 3, name: 'User 3', email: 'arvid@mysite.com'},
            {id: 4, name: 'User 4', email: 'marco@mysite.com'},
            {id: 5, name: 'User 5', email: 'user5@mysite.com'},
            {id: 6, name: 'User 6', email: 'user6@mysite.com'},
        ]);
        $scope.$digest();
    }));


    it('addUser adds a new user to the list of users', function() {
        var usersCountBefore = $scope.cloudSpaceUsers.length;

        $scope.newUser.name = 'User 4';

        var addUserResult = $scope.addUser();
        expect(addUserResult).toBe(true);
        expect($scope.cloudSpaceUsers.length - usersCountBefore).toEqual(1);
        expect(CloudSpace.addUser).toHaveBeenCalled();
        expect($scope.newUser.name).toBeFalsy();
    });

    it("addUser rejects adding a user which doesn't exist", function() {
        var usersCountBefore = $scope.cloudSpaceUsers.length;

        $scope.newUser.name = "User which doesn't exist";

        var addUserResult = $scope.addUser();
        expect(addUserResult).toBe(false);
        expect($scope.cloudSpaceUsers.length).toEqual(usersCountBefore);
    });

});

