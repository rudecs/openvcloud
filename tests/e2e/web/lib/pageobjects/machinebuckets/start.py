from pageobjects.pageobject import PageObject
from newmachine import NewMachine

class Start(PageObject):
    
    def create_machine(self):
        self.waitXpath('//button[@id="singlebutton"]')
        self.driver.find_element_by_id('singlebutton').click()
        return NewMachine(self.driver)