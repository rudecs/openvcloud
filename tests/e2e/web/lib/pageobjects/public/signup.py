from pageobjects.pageobject import PageObject
from pageobjects.machinebuckets.start import Start

class SignUp(PageObject):
    
    def sign_up(self, username, email, password, passwordconfirmation):
        print 'Creating user: \'%s\' with pasword \'%s\'' % (username, password)
        self.driver.find_element_by_id('username').send_keys(username)
        self.driver.find_element_by_id('email').send_keys(email)
        self.driver.find_element_by_id('password_field').send_keys(password)
        self.driver.find_element_by_id('password_field_confirmation').send_keys(passwordconfirmation)
        self.driver.find_element_by_xpath('//input[@type="submit"]').click()
        return Start(self.driver)