import time
import math
from random import randint

class tables():
    def __init__(self, framework):
        self.framework = framework

    def generate_table_elements(self, table):
        table_dict = {'data':'table_%s_data' % table,
                     'info':'table_%s_info' % table,
                     'selector':'table_%s_selector' % table,
                     'pagination':'table_%s_pagination' % table,
                     'search_box':'table_%s_search_box' % table}
        return table_dict

    def get_table_info(self, element):
        for _ in range(10):
            account_info = self.framework.get_text(element)
            if "Showing" in account_info:
                return account_info
            else:
                time.sleep(1)
        else:
            self.framework.fail("Can't get table info")

    def wait_until_table_reload(self, table, page, list_size = 100):
        max_number = self.get_table_max_number(table['info'])
        expected_start_number = min(1+(page*list_size), max_number)
        expected_end_number = min((page+1)*list_size, max_number)
        for _ in range(10):
            start_number = self.get_table_start_number(table['info'])
            end_number = self.get_table_end_number(table['info'])
            if end_number == expected_end_number and start_number == expected_start_number:
                return True
            else:
                time.sleep(1)
        else:
            self.framework.lg('Error expected start & end numbers : %s , actual : %s' %
            (str([expected_start_number, expected_end_number]), str([start_number, end_number])))
            return False

    def get_table_start_number(self, table_info):
        account_info = self.get_table_info(table_info)
        return int(account_info[(account_info.index('g') + 2):(account_info.index('to') - 1)].replace(',', ''))

    def get_table_end_number(self, table_info):
        account_info = self.get_table_info(table_info)
        return int(account_info[(account_info.index('to') + 3):(account_info.index('of') - 1)].replace(',', ''))

    def get_table_max_number(self, table_info):
        account_info = self.get_table_info(table_info)
        return int(account_info[(account_info.index('f') + 2):(account_info.index('entries') - 1)].replace(',',''))

    def get_previous_next_button(self, pagination):
        pagination = self.framework.find_element(pagination)
        pagination = pagination.find_element_by_tag_name('ul')
        pagination = pagination.find_elements_by_tag_name('li')
        previous_button = pagination[0].find_element_by_tag_name('a')
        next_button = pagination[(len(pagination)-1)].find_element_by_tag_name('a')
        return previous_button, next_button

    def get_random_row_from_table(self, table):
        self.framework.assertTrue(self.framework.check_element_is_exist(table['info']))
        max_sort_value = 100
        self.framework.select(table['selector'] , max_sort_value)
        self.wait_until_table_reload(table, 0, max_sort_value)
        time.sleep(10)
        tableData = []
        table_rows = self.framework.get_table_rows(table['data'])
        self.framework.assertTrue(table_rows)
        for row in table_rows:
            cells = row.find_elements_by_tag_name('td')
            tableData.append([x.text for x in cells])
        rows=len(tableData)
        random_elemn= randint(0,rows-1)
        random_row=tableData[random_elemn]
        return random_row

    def get_table_data(self, table, column, max_sort_value = 100):
        self.framework.assertTrue(self.framework.check_element_is_exist(table['info']))
        rows_max_number = self.get_table_max_number(table['info'])
        pages_number = math.ceil(rows_max_number/float(max_sort_value))
        tableData = []
        for page in range(int(pages_number)):
            table_rows = self.framework.get_table_rows(table['data'])
            self.framework.assertTrue(table_rows)
            for row in table_rows:
                cells = row.find_elements_by_tag_name('td')
                tableData.append(cells[column].text)
            if  page < (pages_number-1):
                previous_button, next_button = self.get_previous_next_button(table['pagination'])
                next_button.click()
                if not self.wait_until_table_reload(table, page+1, max_sort_value):
                    self.framework.lg('Error while waiting table to reload')
                    return False

        return tableData

    def check_show_list(self, table):
        table = self.generate_table_elements(table)
        paging_options = [10, 25, 50, 100, 10]
        for option in paging_options:
            self.framework.select(table['selector'], option)
            if not self.wait_until_table_reload(table, 0, option):
                self.framework.lg('option %d does\'nt work as expected' % option)
                return False
            self.framework.lg('option %d passed' % option)

        return True

    def check_next_previous_buttons(self, table):
        table = self.generate_table_elements(table)
        rows_max_number = self.get_table_max_number(table['info'])
        pages_number = math.ceil(rows_max_number/10.0)
        for page in range(int(pages_number)-1):
            page_start_number = self.get_table_start_number(table['info'])
            page_end_number = self.get_table_end_number(table['info'])
            previous_button, next_button = self.get_previous_next_button(table['pagination'])
            next_button.click()
            if not self.wait_until_table_reload(table, page+1, 10):
                self.framework.lg('Error while waiting table to reload after next_1')
                return False
            previous_button, next_button = self.get_previous_next_button(table['pagination'])
            previous_button.click()
            if not self.wait_until_table_reload(table, page, 10):
                self.framework.lg('Error while waiting table to reload after previous')
                return False
            previous_button, next_button = self.get_previous_next_button(table['pagination'])
            next_button.click()
            if not self.wait_until_table_reload(table, page+1, 10):
                self.framework.lg('Error while waiting table to reload after next_2')
                return False

        return True

    def check_sorting_table(self, table):
        table = self.generate_table_elements(table)
        max_sort_value = 100
        self.framework.select(table['selector'] , max_sort_value)
        if not self.wait_until_table_reload(table, 0, max_sort_value):
            self.framework.lg('Error while waiting table to reload')
            return False

        table_location = self.framework.find_element(table['data']).location
        table_head_elements = self.framework.get_table_head_elements(table['data'])
        for column, element in enumerate(table_head_elements):

            if 'sorting_disabled' in element.get_attribute('class'):
                continue

            current_column = element.text
            self.framework.driver.execute_script("window.scrollTo(0,%d)" % (table_location['y']-50))
            element.click()
            self.framework.wait_until_element_attribute_has_text(element, 'aria-sort', 'ascending')
            table_before = self.get_table_data(table, column)

            if table_before == False:
                self.framework.lg('Error while collecting data from column %s after sorting ' % current_column)
                return False
            elif table_before == []:
                self.framework.lg('table is empty')
                return True

            self.framework.driver.execute_script("window.scrollTo(0,%d)" % (table_location['y']-50))
            element.click()
            self.framework.wait_until_element_attribute_has_text(element, 'aria-sort', 'descending')
            table_after = self.get_table_data(table, column)

            if table_after == False:
                self.framework.lg('Error while collecting data from column %s after sorting ' % current_column)
                return False

            if len(table_before) != len(table_after):
                self.framework.lg(('Length of collected data before sorting not equal to the '\
                'length of the collected data after sorting, maybe new item was created during the test'))
                return False

            if table_before != list(reversed(table_after)):
                self.framework.lg('Sorting data in column %s does\'t work as expected' % current_column)
                return False

            self.framework.lg('coulmn %s passed' % current_column)
        return True

    def check_search_box(self, table, column_name):
        table = self.generate_table_elements(table)
        table_head_elements = self.framework.get_table_head_elements(table['data'])
        table_columns = [x.text for x in table_head_elements]
        try:
            column_index = table_columns.index(column_name)
        except ValueError:
            self.framework.lg('table has not column %s' % column_name)
            return False

        random_row = self.get_random_row_from_table(table)
        info_table_before = self.framework.get_text(table['info'])
        if str(random_row[0]) == 'No data available in table':
            self.framework.lg('table is empty')
            return True
        self.framework.set_text(table['search_box'],random_row[column_index])
        time.sleep(5)
        first_row_after = self.framework.get_table_row(table,0)
        if not any(random_row[column_index] in s for s in first_row_after):
            self.framework.lg('searching for value in calumn %s doesn\'t work as expected' % column_name)
            return False
        self.framework.clear_text(table['search_box'])
        if not self.framework.wait_until_element_located_and_has_text(table['info'], info_table_before):
            self.framework.lg("table doesn't update table before search %s and after %s"%(self.framework.get_text(table['info']),info_table_before))
            return False
        return True

    def check_data_filters(self, table, column_name):
        table = self.generate_table_elements(table)
        table_head_elements = self.framework.get_table_head_elements(table['data'])
        table_columns = [x.text for x in  table_head_elements]
        try:
            column_index = table_columns.index(column_name)
        except ValueError:
            self.framework.lg('table has not column %s' % column_name)
            return False

        random_row = self.get_random_row_from_table(table)
        if str(random_row[0]) == 'No data available in table':
            self.framework.lg('table is empty')
            return True

        table_data = self.framework.find_element(table['data'])
        footer = table_data.find_element_by_tag_name('tfoot')
        items = footer.find_elements_by_tag_name('td')
        if 'nofilter' in table_head_elements[column_index].get_attribute('class'):
            return True
        current_filter = items[column_index].find_elements_by_tag_name('input')[0]
        current_filter.send_keys(random_row[column_index])
        time.sleep(5)
        first_row_after = self.framework.get_table_row(table,0)
        if not (random_row[column_index] in first_row_after[column_index]):
            return False
        current_filter.clear()
        return True
