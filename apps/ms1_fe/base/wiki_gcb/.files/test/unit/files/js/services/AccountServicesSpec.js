describe('AccountServices', function() {
    var $httpBackend, Account;

    beforeEach(module('cloudscalers.services'));

    beforeEach(inject(function(_$httpBackend_, _Account_) {
        $httpBackend = _$httpBackend_;
        Account = _Account_;
        defineUnitApiStub($httpBackend);
    }));

    it('can list all accounts', function() {
        var accountsList;
        Account.list().then(function(result) {
            accountsList = result;
        });
    
        expect(accountsList).toBeUndefined();
        $httpBackend.flush();
        expect(accountsList).toBeDefined();
        expect(accountsList.length).toBe(3);
        expect(accountsList[2]).toEqual({id: '4', name: 'Account 4'});
    });
});