import unittest
from nose_parameterized import parameterized
from tests.ovc_master_hosted.Portal.framework.framework import Framework


class PhysicalNodesTests(Framework):
    def setUp(self):
        super(PhysicalNodesTests, self).setUp()
        self.Login.Login(username=self.admin_username, password=self.admin_password)
        self.navigation_bar = 'navigation bar'
        self.lg('go to Physical nodes page')
        self.PhysicalNodes.get_it()
        self.assertTrue(self.PhysicalNodes.is_at())

    def test01_physicalnodes_page_basic_elements(self):
        """
        PRTL-001
        *Test case to make sure the basic elements in Physical nodes page as expected*

        **Test Scenario:**
        #. go to Physical nodes page
        #. check page url & title
        #. check navigation bar
        #. check page title
        #. check 'show records per page' list
        """
        self.lg('check page url & title')
        self.assertEqual(self.driver.title, 'CBGrid - PhysicalNodes')
        self.assertIn('cbgrid/physicalnodes', self.driver.current_url)
        self.lg('check navigation bar')
        self.assertEqual(self.get_navigation_bar(self.navigation_bar), ['Cloud Broker', 'PhysicalNodes'])
        self.lg('check page title')
        self.assertEqual(self.get_text('page title'), 'Physical Nodes')


    def test02_physicalnodes_page_paging_table(self):
        """
        PRTL-002
        *Test case to make sure that show 'records per page' of Physical nodes page is working as expected*

        **Test Scenario:**
        #. go to Physical nodes page.
        #. try paging from the available page numbers and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from the available page numbers and verify it should succeed')
        self.assertTrue(self.Tables.check_show_list('physicalnodes'))
        self.lg('%s ENDED' % self._testID)

    def test03_physicalnodes_page_table_paging_buttons(self):
        """
        PRTL-003
        *Test case to make sure that paging of Physical nodes page is working as expected*

        **Test Scenario:**
        #. go to Physical nodes page.
        #. try paging from start/previous/next/last and verify it should succeed.
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('physicalnodes'))
        self.lg('%s ENDED' % self._testID)