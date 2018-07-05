class home():
    def __init__(self, framework):
        self.framework = framework

    def get_it(self):
        self.framework.lg('Open end user home page')
        self.framework.get_page(self.framework.environment_url)
        self.framework.assertTrue(self.framework.execute_angular_script())
        self.framework.assertTrue(self.framework.wait_until_element_located_and_has_text("end_user_home", "Machines"),
                                  "FAIL: Can't open the end user home page")
