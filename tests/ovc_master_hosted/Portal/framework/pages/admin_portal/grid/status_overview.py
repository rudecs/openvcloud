class statusOverview():
    def __init__(self, framework):
        self.framework = framework

    def get_it(self):
        self.framework.lg('get grid.status_overview page')
        self.framework.LeftNavigationMenu.Grid.status_overview()
        self.framework.assertEqual(self.framework.driver.title, "Grid Status Overview")

    def get_node_status(self):
        node_staus = []
        rows = self.framework.get_table_rows()
        print(rows)
        if rows == False:
            self.framework.lg('There is no rows in this table')
            return False
        for row in rows:
            cells = self.framework.get_row_cells(row)
            if cells == False:
                self.framework.lg('There is no cells in this row')
                return False
            node_staus.append(cells[3].text)
        return node_staus

    def run_health_check(self):
        self.framework.click('Run Healthcheck')
        self.framework.assertEqual(self.framework.get_text('action-RunHealthcheckLabel'),
                                   'Confirm Action Run Health Check')
        self.framework.click('confirm healthcheck')
        self.framework.wait_until_element_located('alert healthcheck')
        return self.framework.get_text('alert healthcheck')
