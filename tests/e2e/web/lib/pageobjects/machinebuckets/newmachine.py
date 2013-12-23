from pageobjects.pageobject import PageObject
from pageobjects.machinebuckets.machinedetails import MachineDetails

class NewMachine(PageObject):
    
    def create(self,name,description, os_type, image_name):
        self.waitXpath('//input[@ng-model="machine.name"]')
        self.driver.find_element_by_xpath('//input[@ng-model="machine.name"]').send_keys(name)
        self.driver.find_element_by_xpath('//textarea[@ng-model="machine.description"]').send_keys(description)
        self.driver.find_element_by_link_text(os_type).click()
        self.driver.find_element_by_xpath('//button[text()="%s"]' % image_name).click()
        
        #And click the Create button
        self.driver.find_element_by_xpath('//button[text()="Create"]').click()
        
        return MachineDetails(self.driver)