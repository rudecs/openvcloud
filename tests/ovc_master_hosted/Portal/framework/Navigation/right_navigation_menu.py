class machines():
    def __init__(self, framework):
        self.framework = framework

    def home(self):
        if self.framework.check_element_is_exist("machines_button"):
            self.framework.lg(" Open machine's page list")
            self.framework.click("machines_button")
            return True
        else:
            self.framework.fail("FAIL : Machine button isn't exist for this user")

    def ceate_machiens(self):
        pass

    def port_forward(self):
        pass

class defence_shield:
    def __init__(self, framework):
        self.framework = framework

    def defence_shiled(self):
        pass


class rightNavigationMenu():
    def __init__(self, framework):
        self.framework = framework
        self.Machines = machines(self.framework)
        self.DefenceShield = defence_shield(self.framework)


