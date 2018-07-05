import time
import unittest
from tests.ovc_master_hosted.Portal.framework.framework import Framework


class CloudspacesTests(Framework):
    def setUp(self):
        super(CloudspacesTests, self).setUp()
        self.Login.Login(cookies_login=True)
        self.navigation_bar = 'navigation bar'
        self.lg('go to cloudspaces page')
        self.CloudSpaces.get_it()
        self.assertTrue(self.CloudSpaces.is_at())

    def test01_cloudspace_page_basic_elements(self):
        """
        PRTL-033
        *Test case to make sure the basic elements in cloudspaces page as expected*

        **Test Scenario:**
        #. go to cloudspaces page
        #. check page url & title
        #. check navigation bar
        #. check page title
        #. check 'show records per page' list
        """
        self.lg('check page url & title')
        self.assertEqual(self.driver.title, 'CBGrid - Cloud Spaces')
        self.assertIn('cbgrid/Cloud%20Spaces', self.driver.current_url)
        self.lg('check navigation bar')
        self.assertEqual(self.get_navigation_bar(self.navigation_bar), ['Cloud Broker','Cloud Spaces'])
        self.lg('check page title')
        self.assertEqual(self.get_text('page title'), 'Cloud Spaces')
        self.lg('check "show records per page" list')
        self.assertTrue(self.element_is_enabled('table_cloudspaces_selector'))

    def test02_cloudspace_page_paging_table(self):
        """ PRTL-034
        *Test case to make sure that paging and sorting of cloudspaces page are working as expected*

        **Test Scenario:**
        #. go to cloudspaces page.
        #. try paging from the available page numbers and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('cloudspaces'))
        self.lg('%s ENDED' % self._testID)


    def test03_cloudspace_page_table_paging_buttons(self):
        """ PRTL-035
        *Test case to make sure that paging and sorting of cloudspaces page are working as expected*

        **Test Scenario:**
        #. go to cloudspaces page.
        #. try paging from start/previous/next/last and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('cloudspaces'))
        self.lg('%s ENDED' % self._testID)

    def test04_cloudspace_page_table_sorting(self):
        """ PRTL-036
        *Test case to make sure that paging and sorting of cloudspaces page are working as expected*

        **Test Scenario:**
        #. go to cloudspaces page.
        #. sorting of all fields of cloudspaces table, should be working as expected
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('sorting of all fields of cloudspaces table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('cloudspaces'))
        self.lg('%s ENDED' % self._testID)
    #
    # def test05_cloudspace_table_search(self):
    #     """
    #     PRTL-037
    #     *Test case to make sure that searching in cloudspaces table is working as expected*
    #
    #     **Test Scenario:**
    #     #. go to cloudspaces page.
    #     #. try general search box to search for values in all columns and verfiy it return the right value
    #     #. try the search box in every column and  verfiy it return the right value
    #     """
    #     self.lg('%s STARTED' % self._testID)
    #     self.lg('try general search box to search for values in all columns and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_search_box('cloudspaces'))
    #     self.lg('try the search box in every column and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_data_filters('cloudspaces'))
    #     self.lg('%s ENDED' % self._testID)
