import unittest
from tests.ovc_master_hosted.Portal.framework.framework import Framework
import time


class AccountsTests(Framework):
    def setUp(self):
        super(AccountsTests, self).setUp()
        self.Login.Login(cookies_login=True)

    def test01_edit_account(self):
        """ PRTL-023
        *Test case to make sure that edit actions on accounts are working as expected*

        **Test Scenario:**
        #. create account.
        #. search for it and verify it should succeed
        #. edit account parameters and verify it should succeed
        """

        self.lg('Create new username, user:%s password:%s' % (self.username, self.password))
        self.Users.create_new_user(self.username, self.password, self.email, self.group)
        self.lg('create new account %s' % self.account)
        self.Accounts.create_new_account(self.account, self.admin_username+"@itsyouonline")
        self.Accounts.open_account_page(self.account)
        self.assertTrue(self.Accounts.account_edit_all_items(self.account))


    def test02_disable_enable_account(self):
        """ PRTL-024
        *Test case to make sure that enable/disable actions on accounts are working as expected*

        **Test Scenario:**
        #. create account.
        #. search for it and verify it should succeed
        #. disable account and verify it should succeed
        #. enable account and verify it should succeed
        """
        self.lg('create new account %s' % self.account)
        self.Accounts.create_new_account(self.account, self.admin_username+"@itsyouonline")
        self.Accounts.open_account_page(self.account)
        self.assertTrue(self.Accounts.account_disable(self.account))
        self.assertTrue(self.Accounts.account_edit_all_items(self.account))
        self.assertTrue(self.Accounts.account_enable(self.account))
        self.assertTrue(self.Accounts.account_edit_all_items(self.account))

    def test03_add_account_with_decimal_limitations(self):
        """ PRTL-026
        *Test case to make sure that creating account with decimal limitations working as expected*

        **Test Scenario:**
        #. create account with decimal limitations.
        #. search for it and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('create new account %s with decimal limitations' % self.account)
        max_memory = '3.5'
        self.Accounts.create_new_account(self.account, self.admin_username+"@itsyouonline", max_memory=max_memory)
        self.Accounts.open_account_page(self.account)
        account_maxmemory = self.get_text("account_page_maxmemory")
        self.assertTrue(account_maxmemory.startswith(max_memory), "Account max memory is [%s]"
                                                                  " and expected is [%s]" % (
                        account_maxmemory, max_memory))

        self.lg('%s ENDED' % self._testID)

    def test04_account_page_paging_table(self):
        """ PRTL-030
        *Test case to make sure that paging and sorting of accounts page are working as expected*

        **Test Scenario:**
        #. go to accounts page.
        #. get number of accounts
        #. try paging from the available page numbers and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.Accounts.get_it()
        self.assertTrue(self.Accounts.is_at())
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('accounts'))
        self.lg('%s ENDED' % self._testID)

    def test05_account_page_table_paging_buttons(self):
        """ PRTL-031
        *Test case to make sure that paging and sorting of accounts page are working as expected*

        **Test Scenario:**
        #. go to accounts page.
        #. get number of accounts
        #. try paging from start/previous/next/last and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.Accounts.get_it()
        self.assertTrue(self.Accounts.is_at())
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('accounts'))
        self.lg('%s ENDED' % self._testID)

    def test06_account_page_table_sorting(self):
        """ PRTL-032
        *Test case to make sure that paging and sorting of accounts page are working as expected*

        **Test Scenario:**
        #. go to accounts page.
        #. get number of accounts
        #. sorting of all fields of accounts table, should be working as expected
        """
        self.lg('%s STARTED' % self._testID)
        self.Accounts.get_it()
        self.assertTrue(self.Accounts.is_at())
        self.lg('sorting of all fields of accounts table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('accounts'))
        self.lg('%s ENDED' % self._testID)

    # def test07_accounts_table_search(self):
    #     """
    #     PRTL-033
    #     *Test case to make sure that searching in accounts table is working as expected*
    #
    #     **Test Scenario:**
    #     #. go to accounts page.
    #     #. try general search box to search for values in all columns and verfiy it return the right value
    #     #. try the search box in every column and  verfiy it return the right value
    #     """
    #     self.lg('%s STARTED' % self._testID)
    #     self.Accounts.get_it()
    #     self.assertTrue(self.Accounts.is_at())
    #     self.lg('try general search box to search for values in all columns and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_search_box('accounts'))
    #     self.lg('try the search box in every column and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_data_filters('accounts'))
    #     self.lg('%s ENDED' % self._testID)
