from pytractor.exceptions import AngularNotFoundException
import time
import pyotp, requests

class login():
    def __init__(self, framework):
        self.framework = framework

    def GetIt(self):
        for _ in range(5):
            self.framework.get_page(self.framework.environment_url)
            time.sleep(5)
            try:
                self.framework.click('landing_page_login')
            except:
                time.sleep(2)
            else:
                break
        else:
            self.framework.click('landing_page_login')
        if not self.IsAt():
            self.framework.fail("The login page isn't loading well.")

    def IsAt(self):
        for temp in range(5):
            if self.framework.wait_until_element_located("username_textbox"):
                return True
            else:
                self.framework.driver.refresh()
        else:
            return False

    def get_GAuth_code(self):
        totp = pyotp.TOTP(self.framework.GAuth_secret)
        GAuth_code = totp.now()
        return GAuth_code

    def Login(self, username='', password='', cookies_login=False):
    
        if cookies_login:       
            self.framework.get_page(self.framework.environment_url)
            cookies = {'name':'beaker.session.id', 'value':self.framework.beaker_session_id}
            self.framework.driver.add_cookie(cookies)
            self.framework.driver.refresh()

        else:      
            username = username or self.framework.admin_username
            password = password or self.framework.admin_password
            self.GetIt()

            self.framework.lg('check the login page title, should succeed')
            self.framework.assertEqual(self.framework.driver.title, 'Log in - It\'s You Online')
            self.framework.lg('Do login using')
            self.framework.set_text('username_textbox', username)
            self.framework.set_text('password_textbox', password)
            self.framework.click('login_button')
            for _ in range(20):
                if 'itsyou.online' in self.framework.driver.current_url:
                    time.sleep(1)
                else:
                    break

            if self.framework.find_elements('authentication_method'):
                if self.framework.get_text(element='authentication_method') == 'Authentication method\nAuthenticator application':
                    self.framework.click('authentication_menu')
                    self.framework.click('authentication_app')
                    self.framework.click('next_button')

            if len(self.framework.find_elements('GAuth_textbox')) > 0:
                self.framework.set_text('GAuth_textbox', self.get_GAuth_code())
                self.framework.click('login_button')
                for _ in range(20):
                    if 'itsyou.online' in self.framework.driver.current_url:
                        time.sleep(1)
                    else:
                        break

            if len(self.framework.find_elements("authorize_button")) > 0:
                self.framework.click('authorize_button')

            for _ in range(25):
                if not self.framework.driver.title:
                    time.sleep(1)
                else:
                    self.framework.assertEqual(self.framework.driver.title, 'OpenvCloud - Decks', "Can't Login")
            self.framework.maximize_window()

    def LoginFail(self, username='', password=''):
        username = username
        password = password
        self.GetIt()
        self.framework.lg('check the login page title, should succeed')
        self.framework.assertEqual(self.framework.driver.title, 'Log in - It\'s You Online')
        self.framework.lg('Do login')
        self.framework.set_text('username_textbox', username)
        self.framework.set_text('password_textbox', password)
        self.framework.click('login_button')
        if password and not username:
            self.framework.assertEqual(self.framework.find_element('username_textbox').get_attribute('aria-invalid'),"true")
            self.framework.assertEqual(self.framework.find_element('password_textbox').get_attribute('aria-invalid'),"false")
        elif username and not password:
            self.framework.assertEqual(self.framework.find_element('password_textbox').get_attribute('aria-invalid'),"true")
            self.framework.assertEqual(self.framework.find_element('username_textbox').get_attribute('aria-invalid'),"false")
        elif not (username and password):
            self.framework.assertEqual(self.framework.find_element('password_textbox').get_attribute('aria-invalid'),"true")
            self.framework.assertEqual(self.framework.find_element('username_textbox').get_attribute('aria-invalid'),"true")
        else:
            self.framework.wait_until_element_located('error_message')
            self.framework.assertEqual(self.framework.find_element('error_message').get_attribute('innerHTML'), "Invalid credentials")
