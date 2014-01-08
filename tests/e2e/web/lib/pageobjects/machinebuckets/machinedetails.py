from pageobjects.pageobject import PageObject

class MachineDetails(PageObject):

    def getMachineName(self):
        return self.driver.find_element_by_xpath('//*[@id="actions"]/div/div[1]/ul/li[1]').text[5:]
    
    def getIp(self):
        return self.driver.find_element_by_xpath('//**[@id="actions"]/div/div[1]/ul/li[2]').text[5:]
        

    def stop(self):
        pass