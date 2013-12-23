import unittest
import os
import random
from selenium import webdriver
from pageobjects.public import menu as publicmenu

class TestSignup(unittest.TestCase):
         
    def getDriver(self, browser):
        browsers = {'IE': webdriver.Ie, 'Chrome': webdriver.Chrome, 'Firefox': webdriver.Firefox}
        return browsers[browser]()

    def setUp(self):
        self.env_url = os.environ.get('env_url', "http://10.101.190.25/wiki_gcb/")
        self.driver = self.getDriver(os.environ.get('browser', 'Firefox'))
        self.driver.get(self.env_url)
        self.driver.maximize_window()
                
    def tearDown(self):
        self.driver.quit()

    def test_non_existing_user(self):
        signup_page = publicmenu.Menu(self.driver).sign_up()
        username = 'rob%s' % random.randint(1,999999999999)
        machinebuckets = signup_page.sign_up(username, username + '@incubaid.com', 'secret', 'secret')
        machinedetails = machinebuckets.create_machine().create('testmachine',
                                               'This is a machine generated during an automated e2e test.',
                                               'Ubuntu', 'Linux 13.04 image')
        
        pass
    

if __name__ == '__main__':
    unittest.main()
