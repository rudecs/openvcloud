from selenium.webdriver.support.ui import WebDriverWait

class PageObject(object):
    def __init__(self, driver):
        self.debug = True
        self.driver = driver
        self.TIMEOUT = 30
        self.wait = WebDriverWait(self.driver, self.TIMEOUT, 10)

    def get(self, cssSelector):
        if self.debug:
            print "Getting %s" % cssSelector
        return self.driver.find_element_by_css_selector(cssSelector)

    def waitCss(self, cssSelector):
        if self.debug:
            print "Waiting Css %s" % cssSelector
        return self.wait.until(lambda driver: driver.find_element_by_css_selector(cssSelector))

    def waitXpath(self, xpath):
        if self.debug:
            print "Waiting Xpath %s" % xpath
        return self.wait.until(lambda driver: driver.find_elements_by_xpath(xpath))

    def waitForMany(self, cssSelector):
        if self.debug:
            print "Waiting For Many %s" % cssSelector
        try:
            return self.wait.until(lambda driver : driver.find_elements_by_css_selector(cssSelector))
        except:
            return []

