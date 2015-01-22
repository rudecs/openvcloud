describe("CloudSpaceNavigatorController", function(){
    var $scope, navigatorCtrl, sessionCtrl, $q, CloudSpace, Account, $modal;
    beforeEach(module('cloudscalers'));

    beforeEach(inject(function($rootScope, _$controller_, _$q_) {
        $controller = _$controller_;
        
        $scope = $rootScope.$new();
        $q = _$q_;

		$modal = {
			open: jasmine.createSpy('$modal.open')
		};
        var cloudListDefer = $q.defer();
        var accountListDefer = $q.defer();

        CloudSpace = {
            current : jasmine.createSpy('current'), 
            setCurrent : jasmine.createSpy('setCurrent'), 
            list: jasmine.createSpy('list').andReturn(cloudListDefer.promise),
            create: jasmine.createSpy('create').andReturn($q.defer().promise)
        };

        Account = {
            list: jasmine.createSpy('list').andReturn(accountListDefer.promise)
        };
        
        sessionCtrl = $controller('AuthenticatedSessionController', {
            $scope: $scope,
            CloudSpace: CloudSpace,
            Account: Account
        });
        navigatorCtrl = $controller('CloudSpaceNavigatorController', {$scope : $scope, $modal: $modal, CloudSpace: CloudSpace});
        cloudListDefer.resolve([
                               {cloudSpaceId: 2, accountId: 1},
                               {cloudSpaceId: 3, accountId: 2},
                               ]);
        accountListDefer.resolve([
                                 {id: 1, name: 'Account 1'},
                                 {id: 2, name: 'Account 2'}
                                 ]);
    }));

    it('builds accounts & cloudspaces hierarchy from lists of cloudspaces & accounts', function() {
        expect($scope.AccountCloudSpaceHierarchy).toBeUndefined();
        $scope.$digest();
        expect($scope.AccountCloudSpaceHierarchy).toEqual([
            {id: 1, name: 'Account 1', cloudspaces: [{cloudSpaceId: 2, accountId: 1}]},
            {id: 2, name: 'Account 2', cloudspaces: [{cloudSpaceId: 3, accountId: 2}]}
        ]);
    });
    
    describe('New CloudSpace tests', function(){
    	
    	
    	it('calls CloudSpace service with correct parameters', function(){
    		var newCloudSpaceName = 'myawesome new cloudspace number ' + Math.random();
 	    	$scope.currentUser = {username:'Lenny'}
    		var dialogresult = $q.defer();
 	    	
 	    	$modal.open.andReturn({result:dialogresult.promise});
 	    	
 	    	$scope.createNewCloudSpace();
 	    	
 	    	expect(CloudSpace.create).not.toHaveBeenCalled();
 	    	
 	    	$scope.$apply(function() {	
 	    		dialogresult.resolve({name:newCloudSpaceName, accountId:78 });
 	    	});
 	    	
 	    	expect(CloudSpace.create).toHaveBeenCalledWith(newCloudSpaceName, 78, 'Lenny');	
    	});
    	
    });



});