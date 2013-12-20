from pageobjects.pageobject import PageObject
from pageobjects.public.signup import SignUp

class Menu(PageObject):
    def go_to(self):
        pass
    
    def sign_up(self):
        signuplink = self.driver.find_element_by_link_text('Sign Up')
        signuplink.click()
        return SignUp(self.driver)