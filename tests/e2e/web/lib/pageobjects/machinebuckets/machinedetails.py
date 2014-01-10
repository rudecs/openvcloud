from pageobjects.pageobject import PageObject

class MachineDetails(PageObject):

    def getMachineName(self):
        return self.driver.find_element_by_xpath('//*[@id="actions"]/div/div[1]/ul/li[1]/div/div').text
    
    def getIP(self):
        return self.driver.find_element_by_xpath('//*[@id="actions"]/div/div[1]/ul/li[3]/div/div').text
        
    def stop(self):
        pass
    
    def clone(self, clonename):
        pass