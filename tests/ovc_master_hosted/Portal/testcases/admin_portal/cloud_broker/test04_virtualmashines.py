import time
import unittest
from tests.ovc_master_hosted.Portal.framework.framework import Framework

class VirtualMachinesTest(Framework):

    def setUp(self):
        super(VirtualMachinesTest, self).setUp()
        self.Login.Login(cookies_login=True)
        self.navigation_bar = 'navigation bar'
        self.lg('go to virtual machines page')
        self.VirtualMachines.get_it()
        self.assertTrue(self.VirtualMachines.is_at())

    def test01_cloudspace_page_basic_elements(self):
        """
        PRTL-042
        *Test case to make sure the basic elements in virtual machines page as expected*

        **Test Scenario:**
        #. go to virtual machines page
        #. check page url & title
        #. check navigation bar
        #. check page title
        #. check 'show records per page' list
        """
        self.lg('check page url & title')
        self.assertEqual(self.driver.title, 'CBGrid - Virtual Machines')
        self.assertIn('cbgrid/Virtual%20Machines', self.driver.current_url)
        self.lg('check navigation bar')
        self.assertEqual(self.get_navigation_bar(self.navigation_bar), ['Cloud Broker','Virtual Machines'])
        self.lg('check page title')
        self.assertEqual(self.get_text('page title'), 'Virtual Machines')
        self.lg('check "show records per page" list')
        self.assertTrue(self.element_is_enabled('table_machines_selector'))

    def test02_vm_page_paging_table(self):
        """ PRTL-043
        *Test case to make sure that paging and sorting of vms page are working as expected*

        **Test Scenario:**
        #. go to vms page.
        #. try paging from the available page numbers and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('machines'))
        self.lg('%s ENDED' % self._testID)


    def test03_vms_page_table_paging_buttons(self):
        """ PRTL-044
        *Test case to make sure that paging and sorting of vms page are working as expected*

        **Test Scenario:**
        #. go to vms page.
        #. try paging from start/previous/next/last and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('machines'))
        self.lg('%s ENDED' % self._testID)

    def test04_vms_page_table_sorting(self):
        """ PRTL-045
        *Test case to make sure that paging and sorting of vms page are working as expected*

        **Test Scenario:**
        #. go to vms page.
        #. sorting of all fields of vms table, should be working as expected
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('sorting of all fields of vms table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('machines'))
        self.lg('%s ENDED' % self._testID)

    # def test05_vms_table_search(self):
    #     """
    #     PRTL-046
    #     *Test case to make sure that searching in vms table is working as expected*
    #
    #     **Test Scenario:**
    #     #. go to vms page.
    #     #. try general search box to search for values in all columns and verfiy it return the right value
    #     #. try the search box in every column and  verfiy it return the right value
    #     """
    #     self.lg('%s STARTED' % self._testID)
    #     self.lg('try general search box to search for values in all columns and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_search_box('machines'))
    #     self.lg('try the search box in every column and verfiy it return the right value')
    #     self.assertTrue(self.Tables.check_data_filters('machines'))
    #     self.lg('%s ENDED' % self._testID)
