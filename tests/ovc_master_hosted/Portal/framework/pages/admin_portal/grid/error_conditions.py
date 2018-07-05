class errorConditions():
    def __init__(self, framework):
        self.framework = framework

    def get_it(self):
        self.framework.lg('get grid.error_conditions page')
        self.framework.LeftNavigationMenu.Grid.error_conditions()
        self.framework.assertTrue(self.framework.check_element_is_exist("error_conditions_page"))


