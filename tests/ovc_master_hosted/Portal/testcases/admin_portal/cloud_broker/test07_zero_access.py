import unittest
from nose_parameterized import parameterized
from tests.ovc_master_hosted.Portal.framework.framework import Framework

class ZeroAccessTests(Framework):
    def setUp(self):
        super(ZeroAccessTests, self).setUp()
        self.Login.Login(cookies_login=True)
        self.navigation_bar = 'navigation bar'
        self.lg('go to zero access page')
        self.ZeroAccess.get_it()
        self.assertTrue(self.ZeroAccess.is_at())

    def test01_zero_access_page_basic_elements(self):
        """
        PRTL-001
        *Test case to make sure the basic elements in zero access page as expected*

        **Test Scenario:**
        #. go to zero access page
        #. check page url & title
        #. check navigation bar
        #. check page title
        #. check 'show records per page' list
        """
        self.lg('check page url & title')
        self.assertEqual(self.driver.title, 'CBGrid - 0-access')
        self.assertIn('cbgrid/0-access', self.driver.current_url)
        self.lg('check navigation bar')
        self.assertEqual(self.get_navigation_bar(self.navigation_bar), ['Cloud Broker', '0-access'])

    def test02_zero_access_nodes_table_paging(self):
        """
        PRTL-002
        *Test case to make sure that show 'records per page' of zero access nodes's table is working as expected*

        **Test Scenario:**
        #. go to zero access page.
        #. try paging from the available page numbers and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('zero_access_nodes'))
        self.lg('%s ENDED' % self._testID)

    def test03_zero_access_nodes_table_paging_buttons(self):
        """
        PRTL-003
        *Test case to make sure that paging of zero access nodes's table is working as expected*

        **Test Scenario:**
        #. go to zero access page.
        #. try paging from start/previous/next/last and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('zero_access_nodes'))
        self.lg('%s ENDED' % self._testID)

    def test04_zero_access_sessions_table_paging(self):
        """
        PRTL-004
        *Test case to make sure that show 'records per page' of zero access sessions's table is working as expected*

        **Test Scenario:**
        #. go to zero access page.
        #. try paging from the available page numbers and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('zero_access_sessions'))
        self.lg('%s ENDED' % self._testID)

    def test05_zero_access_sessions_table_paging_buttons(self):
        """
        PRTL-005
        *Test case to make sure that paging of zero access sessions's table is working as expected*

        **Test Scenario:**
        #. go to storage routers page.
        #. try paging from start/previous/next/last and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('zero_access_sessions'))
        self.lg('%s ENDED' % self._testID)