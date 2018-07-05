import time
import unittest
from tests.ovc_master_hosted.Portal.framework.framework import Framework


class UsersTests(Framework):

    def setUp(self):
        super(UsersTests, self).setUp()
        self.Login.Login(cookies_login=True)
        self.navigation_bar = 'navigation bar'
        self.lg('go to users page')
        self.Users.get_it()
        self.assertTrue(self.Users.is_at())

    def test01_users_page_basic_elements(self):
        """
        PRTL-001
        *Test case to make sure the basic elements in storage routers page as expected*

        **Test Scenario:**
        #. go to users page
        #. check page url & title
        #. check navigation bar
        #. check page title
        #. check 'show records per page' list
        """
        self.lg('check page url & title')
        self.assertEqual(self.driver.title, 'CBGrid - Users')
        self.assertIn('cbgrid/users', self.driver.current_url)
        self.lg('check navigation bar')
        self.assertEqual(self.get_navigation_bar(self.navigation_bar), ['Cloud Broker','Users'])
        self.lg('check page title')
        self.assertEqual(self.get_text('page title'), 'Users')
        self.lg('check "show records per page" list')
        self.assertTrue(self.element_is_enabled('table_users_selector'))

    def test02_users_page_paging_table(self):
        """ PRTL-039
        *Test case to make sure that paging and sorting of users page are working as expected*

        **Test Scenario:**
        #. go to users page.
        #. try paging from the available page numbers and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('users'))
        self.lg('%s ENDED' % self._testID)

    def test03_users_page_table_paging_buttons(self):
        """ PRTL-040
        *Test case to make sure that paging and sorting of users page are working as expected*

        **Test Scenario:**
        #. go to users page.
        #. try paging from start/previous/next/last and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('users'))
        self.lg('%s ENDED' % self._testID)

    def test04_users_page_table_sorting(self):
        """ PRTL-041
        *Test case to make sure that paging and sorting of users page are working as expected*

        **Test Scenario:**
        #. go to users page.
        #. sorting of all fields of users table, should be working as expected
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('sorting of all fields of users table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('users'))
        self.lg('%s ENDED' % self._testID)
        
