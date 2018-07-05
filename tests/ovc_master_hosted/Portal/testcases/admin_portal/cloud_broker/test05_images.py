import time
import unittest
from tests.ovc_master_hosted.Portal.framework.framework import Framework
from nose_parameterized import parameterized
from random import *


class ImagesTests(Framework):
    def setUp(self):
        super(ImagesTests, self).setUp()
        self.Login.Login(cookies_login=True)

    def test01_image_page_paging_table(self):
        """ PRTL-041
        *Test case to make sure that paging and sorting of image  page are working as expected*

        **Test Scenario:**cd
        #. go to Images page.
        #. get number of images
        #. try paging from the available page numbers and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('1- go to Images page')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        self.lg('2- try paging from the available page numbers and verify it should succeed ')
        self.assertTrue(self.Tables.check_show_list('images'))

    def test02_image_page_table_sorting(self):
        """ PRTL-042
        *Test case to make sure that paging and sorting of images page are working as expected*

        **Test Scenario:**
        #. go to image page.
        #. get all table head elements
        #. sorting of all fields of images table, should be working as expected
        """
        self.lg('%s STARTED' % self._testID)
        self.lg('- go to image bage')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        self.assertTrue(self.Tables.check_sorting_table('images'))

    def test03_image_page_table_paging_buttons(self):
        """ PRTL-043
        *Test case to make sure that paging and sorting of images page are working as expected*

        **Test Scenario:**

        #. go to images page.
        #. get number of images
        #. try paging from start/previous/next/last and verify it should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        self.assertTrue(self.Tables.check_next_previous_buttons('images'))

    @parameterized.expand(['Name',
                           'Status'])
    def test04_image_page_searchbox(self, column):
        """ PRTL-044
        *Test case to make sure that search boxes of images page are working as expected*

        **Test Scenario:**

        #. go to images page.
        #. try use the search box in every column and  verfiy it return the right value
        """
        self.lg('1- go to Images page')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        self.lg('try the search box in every column and verfiy it return the right value')
        self.assertTrue(self.Tables.check_data_filters('images', column))

    def test05_stack_table_in_image_page_test(self):
        """ PRTL-045

        **Test Scenario:**

        #. go to images page.
        #. open random image page
        #. get number of stacks
        #. try paging from the available page numbers in stack table  and verify it should succeed
        #. sorting of all fields of virtual machine table, should be working as expected
        #. try paging from start/previous/next/last and verify it should succeed
        """
        self.lg('- go to Images page')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        image = choice(['Ubuntu', 'Windows'])
        self.Images.open_image_page(image=image)
        self.lg('-  try paging from the available page numbers and verify it should succeed ')
        self.assertTrue(self.Tables.check_show_list('stacks'))
        self.lg('- sorting of all fields of stack table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('stacks'))
        self.lg('- try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('stacks'))

    def test06_VM_table_in_image_page_test(self):
        """ PRTL-046

        **Test Scenario:**

        #. go to images page.
        #. open random image page
        #. get number of vms
        #. try paging from the available page numbers in stack table  and verify it should succeed
        #. sorting of all fields of virtual machine table, should be working as expected
        #. try paging from start/previous/next/last and verify it should succeed
        """
        self.lg('1- go to Images page')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        image = choice(['Ubuntu', 'Windows'])
        self.Images.open_image_page(image=image)
        self.lg('-  try paging from the available page numbers and verify it should succeed ')
        self.assertTrue(self.Tables.check_show_list('machines'))
        self.lg('- sorting of all fields of stack table, should be working as expected')
        self.assertTrue(self.Tables.check_sorting_table('machines'))
        self.lg('- try paging from start/previous/next/last and verify it should succeed')
        self.assertTrue(self.Tables.check_next_previous_buttons('machines'))

    @parameterized.expand(['ID',
                           'Grid ID',
                           'Name',
                           'Status',
                           'Reference ID'])
    def test07_search_boxes_in_stack_in_image_page_test(self, column):
        """ PRTL-047
        *Test case to make sure that search boxes of stack table  image page are working as expected*

        **Test Scenario:**

        #. go to images page.
        #. open one random  image page
        #. try use the search box in every column and  verfiy it return the right value in stack table
        """
        self.lg('1- go to Images page')
        self.Images.get_it()
        image = choice(['Ubuntu', 'Windows'])
        self.Images.open_image_page(image=image)
        self.lg('try the search box in every column and verfiy it return the right value')
        self.assertTrue(self.Tables.check_data_filters('stacks', column))

    @parameterized.expand(['Name',
                           'Hostname',
                           'Status',
                           'Cloud Space',
                           'Stack ID']
                          )
    def test08_search_boxes_in_VM_in_image_page_test(self, column):
        """ PRTL-048
        *Test case to make sure that search boxes of VM table in image page  are working as expected*
        
        **Test Scenario:**

        #. go to images page.
        #. open one random  image page
        #. try use the search box in every column and  verfiy it return the right value in VM table
        """
        self.lg('1- go to Images page')
        self.Images.get_it()
        self.assertTrue(self.Images.is_at())
        image = choice(['Ubuntu', 'Windows'])
        self.Images.open_image_page(image=image)
        self.lg('3-try the search box in every column and verfiy it return the right value')
        self.assertTrue(self.Tables.check_data_filters('machines', column))
