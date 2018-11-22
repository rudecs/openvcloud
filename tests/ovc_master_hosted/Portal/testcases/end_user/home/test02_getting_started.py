from tests.ovc_master_hosted.Portal.framework.framework import Framework


class QuickTutorialGuide(Framework):

    def setUp(self):
        super(QuickTutorialGuide, self).setUp()
        self.Login.Login(cookies_login=True, portal='enduser')
        self.click("getting_started_button")

    def test01_intro(self):
        """ PRTL-006
        *Test case for check user potal intro tab.*

        **Test Scenario:**

        #. check all intro page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.click("intro_tab")
        self.assertEqual(self.get_text("intro_header_label"),
                         "Welcome to your OpenvCloud Cloud Space!")
        self.assertEqual(self.get_text("intro_line1_label"),
                         "Before you start, maybe some things that are good to know:")
        self.assertEqual(self.get_text("intro_line2_label"),
                         "The Cloud Space provides access to different Cloud Decks:")
        self.assertEqual(self.get_text("intro_line3_label"),
                         "Machines: Virtual Machines creation and management via the "
                         "web portal or API.")
        self.assertEqual(self.get_text("intro_line4_label"),
                         "The Cloud Space is protected by the Defense Shield, your "
                         "personal firewall that handles all incoming and outgoing "
                         "traffic for your Cloud Space, your routing, "
                         "port fowards and firewall settings.")
        self.assertEqual(self.get_text("intro_subheader_label"),
                         "Questions?")
        self.assertEqual(self.get_text("intro_line5_label"),
                         "In case of any questions, go to our Documentation Center or "
                         "contact Support")
        self.assertEqual(self.element_link("intro_spport_link"),
                        "%s/g8vdc/#/Support" % self.environment_url.replace('http:', 'https:'))
        self.lg('%s ENDED' % self._testID)

    def test02_cloudspace(self):
        """ PRTL-007
        *Test case for check user potal cloudspace tab.*

        **Test Scenario:**

        #. check all cloudspace page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.click("cloudspace_tab")
        self.assertEqual(self.get_text("cloudspace_header_label"),
                         "Cloud Space")
        self.assertEqual(self.get_text("cloudspace_line1_label"),
                         "Optionally Go to Cloud Space Settings to provide access to other "
                         "registered users in the OpenvCloud cloud.")
        self.assertEqual(self.get_text("cloudspace_line2_label"),
                         "Optionally create an additional Cloud Space, allowing you to divide "
                         "your resources into 2 private networks, managed from the same portal!")
        self.assertEqual(self.get_text("cloudspace_subheader_label"),
                         "Questions?")
        self.assertEqual(self.get_text("cloudspace_line3_label"),
                         "In case of any questions, go to our Documentation Center or contact "
                         "Support")
        self.assertEqual(self.element_link("cloudspace_spport_link"),
                        "%s/g8vdc/#/Support" % self.environment_url.replace('http:', 'https:'))
        self.lg('%s ENDED' % self._testID)

    def test03_machines(self):
        """ PRTL-008
        *Test case for check user potal machines tab.*

        **Test Scenario:**

        #. check all machines page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.click("machines_tab")
        self.assertEqual(self.get_text("machines_header_label"),
                         "Machines")
        self.assertEqual(self.get_text("machines_line1_label"),
                         "Click on Machines, hit Create Machine")
        self.assertEqual(self.get_text("machines_line2_label"),
                         "Set the name for your Virtual Machine")
        self.assertEqual(self.get_text("machines_line3_label"),
                         "Choose one of the packages, delivering CPU, RAM and 10GB SSD")
        self.assertEqual(self.get_text("machines_line4_label"),
                         "Expand your SSD size")
        self.assertEqual(self.get_text("machines_line5_label"),
                         "Hit Create")
        self.assertEqual(self.get_text("machines_line6_label"),
                         "Go to Console tab")
        self.assertEqual(self.get_text("machines_line7_label"),
                         "Login and take control (Windows Images need to load some minutes "
                         "to finish all initalisations before you can login)")
        self.assertEqual(self.get_text("machines_line8_label"),
                         "After maximum a few minutes you will see the IP address that will "
                         "be provisioned by your Defense Shield. By default this is a private "
                         "IP address")
        self.assertEqual(self.get_text("machines_line9_label"),
                         "Use the Port Fowards in the Machines submenu page to quickly enable "
                         "public access to a specific port of your virtual machine")
        self.assertEqual(self.get_text("machines_line10_label"),
                         "Your virtual machine is charged once created per hour, for minimal "
                         "an hour. You can delete anytime and the charging stops.")
        self.assertEqual(self.get_text("machines_subheader_label"),
                         "Questions?")
        self.assertEqual(self.get_text("machines_line11_label"),
                         "In case of any questions, go to our Documentation Center or contact "
                         "Support")
        self.assertEqual(self.element_link("machines_spport_link"),
                        "%s/g8vdc/#/Support" % self.environment_url.replace('http:', 'https:'))
        self.lg('%s ENDED' % self._testID)

    def test04_defense_shield(self):
        """ PRTL-009
        *Test case for check user potal defense shield tab.*

        **Test Scenario:**

        #. check all defense shield page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.click("defense_shield_tab")
        self.assertEqual(self.get_text("defense_shield_header_label"),
                         "Defense Shield")
        self.assertEqual(self.get_text("defense_shield_line1_label"),
                         "Go to Defense Shield")
        self.assertEqual(self.get_text("defense_shield_line2_label"),
                         "Login with user 'admin' and your portal password")
        self.assertEqual(self.get_text("defense_shield_line3_label"),
                         "Configure what you like, it`s private it`s yours")
        self.assertEqual(self.get_text("defense_shield_line4_label"),
                         "Each Cloud Space has its own Defense Shield")
        self.assertEqual(self.get_text("defense_shield_line5_label"),
                         "For more simple tasks, use the Port Fowards in the Machines submenu")
        self.assertEqual(self.get_text("defense_shield_subheader_label"),
                         "Questions?")
        self.assertEqual(self.get_text("defense_shield_line6_label"),
                         "In case of any questions, go to our Documentation Center or contact "
                         "Support")
        self.assertEqual(self.element_link("defense_shield_spport_link"),
                        "%s/g8vdc/#/Support" % self.environment_url.replace('http:', 'https:'))
        self.lg('%s ENDED' % self._testID)
