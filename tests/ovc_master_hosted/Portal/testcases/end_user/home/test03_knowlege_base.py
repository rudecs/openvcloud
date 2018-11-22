from tests.ovc_master_hosted.Portal.framework.framework import Framework


class KnowledgeBase(Framework):

    def __init__(self, *args, **kwargs):
        super(KnowledgeBase, self).__init__(*args, **kwargs)

    def setUp(self):
        super(KnowledgeBase, self).setUp()
        self.Login.Login(cookies_login=True, portal='enduser')
        self.click("knowledge_base_button")

    def test01_technical_tutorials(self):
        """ PRTL-010
        *Test case for check user potal technical tutorials.*

        **Test Scenario:**

        #. check all technical tutorials page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line1_tab"),
                         "Access your Cloud Space using OpenVPN")
        self.assertEqual(self.get_text("knowledge_base_line2_tab"),
                         "How to configure Ubuntu to connect to OpenVPN")
        self.assertEqual(self.get_text("knowledge_base_line3_tab"),
                         "My First Machine Linux")
        self.assertEqual(self.get_text("knowledge_base_line4_tab"),
                         "Enable Root access on ubuntu over SSH")
        self.assertEqual(self.get_text("knowledge_base_line5_tab"),
                         "My First Machine Windows")
        self.assertEqual(self.get_text("knowledge_base_line6_tab"),
                         "PPTP Connection To Space From Windows 10")
        self.assertEqual(self.get_text("knowledge_base_line7_tab"),
                         "Using the API")
        self.assertEqual(self.get_text("knowledge_base_subheader_label"),
                         "Welcome")
        self.assertEqual(self.get_text("knowledge_base_subheader_email"),
                         "support@greenitglobe.com")
        self.assertEqual(self.get_text("knowledge_base_subheader_text"),
                         "Welcome to the OpenvCloud Knowledge Base. The Knowledge Base is "
                         "growing based on customer questions. In case you do not find a reply, "
                         "do not hesistate to contact the support team at: "
                         "support@greenitglobe.com.")
        self.lg('%s ENDED' % self._testID)

    def test02_technical_tutorials_first_tab(self):
        """ PRTL-011
        *Test case for check user potal technical tutorials first tab.*

        **Test Scenario:**

        #. check all technical tutorials first tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line1_tab"),
                         "Access your Cloud Space using OpenVPN")
        self.click("knowledge_base_line1_tab")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_header"),
                         "Access your Cloud Space using OpenVPN")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line1"),
                         "Go to: OpenVPN Downloads Page.")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line2"),
                         "Choose your installer according to your architect \"Windows Installer "
                         "(32-bit)|Windows Installer (64-bit)\".")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line3"),
                         "Right-click on the installer and choose: \"Run as administrator\"")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line4"),
                         "Press \"Yes\" in the confirmation windows")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line5"),
                         "Click \"Next\" on the welcome page")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line6"),
                         "Click \"I Agree\" on the license page")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line7"),
                         "Click \"Next\" for the default components")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line8"),
                         "Click \"Install\"")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line9"),
                         "Click \"Next\" after the installation in completed")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line10"),
                         "Download our OpenVPN configuration zip from the Network Deck")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line11"),
                         "Unzip the \"OpenVPN configuration zip\" at: \"C:Program Files"
                         "OpenVPNconfig\"")
        self.assertEqual(self.get_text("knowledge_base_line1_tab_line12"),
                         "Right-click on the \"OpenVPN GUI\" icon and choose: \"Run as "
                         "administrator\".")
        self.lg('%s ENDED' % self._testID)

    def test03_technical_tutorials_second_tab(self):
        """ PRTL-012
        *Test case for check user potal technical tutorials second tab.*

        **Test Scenario:**

        #. check all technical tutorials second tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line2_tab"),
                         "How to configure Ubuntu to connect to OpenVPN")
        self.click("knowledge_base_line2_tab")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_header"),
                         "How to configure Ubuntu to connect to OpenVPN")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line1"),
                         "Open Terminal\nIn Unity\nDash -> Search for Terminal\nIn Gnome\n"
                         "Application menu -> Accessories -> Terminal\nor\n"
                         "Keyboard Shortcut: Ctrl + Alt + T")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line2"),
                         "Run the following command apt-get install network-manager-openvpn")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line3"),
                         "Right-click on the network icon on the system tray")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line4"),
                         "Choose: \"Edit Connections\"")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line5"),
                         "Click Add")
        self.assertTrue(self.wait_element("knowledge_base_line2_tab_image5"))
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line6"),
                         "Choose Connection Type : openvpn")
        self.assertTrue(self.wait_element("knowledge_base_line2_tab_image6"))
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7"),
                         "The following window will open:")
        self.assertTrue(self.wait_element("knowledge_base_line2_tab_image7"))
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub1"),
                         "Enter the connection name as example \"VPN connection\"")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub2"),
                         "Enter the Gateway")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub3"),
                         "Under the Authentication -> Type -> choose Passowrd")
        self.assertTrue(self.wait_element("knowledge_base_line2_tab_line7_image3"))
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub4"),
                         "Download our CA certificate")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub5"),
                         "Enter the username and the passowrd")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line7_sub6"),
                         "Import the CA certificate you just downloaded")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line8"),
                         "Click \"Advanced\" the following window will open:")
        self.assertTrue(self.wait_element("knowledge_base_line2_tab_image8"))
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line8_sub1"),
                         "Set \"Use Custom gateway port \" to 999")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line8_sub2"),
                         "Mark \"Use a TCP connection\"")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line8_sub3"),
                         "Click \"OK\" and then Save")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line9"),
                         "Right-click on the network icon on the system tray")
        self.assertEqual(self.get_text("knowledge_base_line2_tab_line10"),
                         "Choose \" VPN Connection then choose the new connection")
        self.lg('%s ENDED' % self._testID)

    def test04_technical_tutorials_third_tab(self):
        """ PRTL-013
        *Test case for check user potal technical tutorials third tab.*

        **Test Scenario:**

        #. check all technical tutorials third tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line3_tab"),
                         "My First Machine Linux")
        self.click("knowledge_base_line3_tab")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_header"),
                         "My First Machine Linux")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line1"),
                         "Login to the OpenvCloud User Portal:")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image1"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line2"),
                         "To create a virtual machine go to Machines, and click on"
                         " 'Create Machine'")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image2"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line3"),
                         "Select your properties in this example:")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line3_sub1"),
                         "Ubuntu 14.04 64 bit")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line3_sub2"),
                         "1 GB memory")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line3_sub3"),
                         "Std disk size")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image3"))
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image4"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line4"),
                         "Within seconds the machine is active.")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image5"))
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image6"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line5"),
                         "Unlike other clouds, OpenvCloud puts every virtual machine "
                         "behind a private firewall.")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line6"),
                         "To have access to your virtual machine you can create a VPN "
                         "connection (see other tutorials) or configure a")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line7"),
                         "port forwarding (means forward a port from your private firewall "
                         "to the port on your virtual machine).")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line8"),
                         "Here we will choose for the later option.")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line9"),
                         "In order to configure the port forwarding, click on Port Forwards tab:")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image7"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line10"),
                         "Click the Add button, and specify that you want to forward port 3022 "
                         "to you port 22 on your virtual machine:")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image8"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line11"),
                         "As a result you will see the below:")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image9"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line12"),
                         "We will now use an ssh client to connect to the virtual machine "
                         "e.g. putty")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image10"))
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image11"))
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image12"))
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image13"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line14"),
                         "Congrats, you are on your machine.")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_header1"),
                         "Tip 1")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line15"),
                         "To change password of root user do sudo passwd root")
        self.assertTrue(self.wait_element("knowledge_base_line3_tab_image14"))
        self.assertEqual(self.get_text("knowledge_base_line3_tab_header2"),
                         "Tip 2")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line16"),
                         "To connect over ssh you always need to login as cloudscalers and then "
                         "use sudo -s to get root access.")
        self.assertEqual(self.get_text("knowledge_base_line3_tab_line17"),
                         "You can now deploy whatever apps & through port forwarding (like done "
                         "above) give access to your apps.")
        self.lg('%s ENDED' % self._testID)

    def test05_technical_tutorials_forth_tab(self):
        """ PRTL-014
        *Test case for check user potal technical tutorials forth tab.*

        **Test Scenario:**

        #. check all technical tutorials forth tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line4_tab"),
                         "Enable Root access on ubuntu over SSH")
        self.click("knowledge_base_line4_tab")
        self.assertEqual(self.get_text("knowledge_base_line4_tab_header"),
                         "Enable Root access on ubuntu over SSH")
        self.assertEqual(self.get_text("knowledge_base_line4_tab_line1"),
                         "Create new password for root")
        self.assertEqual(self.get_text("knowledge_base_line4_tab_line2"),
                         "Enabling root login from ssh config (default is to deny root access)")
        self.assertEqual(self.get_text("knowledge_base_line4_tab_line3"),
                         "Restarting ssh:")
        self.lg('%s ENDED' % self._testID)

    def test06_technical_tutorials_fifth_tab(self):
        """ PRTL-015
        *Test case for check user potal technical tutorials fifth tab.*

        **Test Scenario:**

        #. check all technical tutorials fifth tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line5_tab"),
                         "My First Machine Windows")
        self.click("knowledge_base_line5_tab")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_header"),
                         "My First Machine Windows")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line1"),
                         "Login to the OpenvCloud User Portal:")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image1"))
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image2"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line3"),
                         "Select your properties in this example:")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line3_sub1"),
                         "Windows 2012r2 Standard")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line3_sub2"),
                         "1 GB memory, 1 core(s)")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line3_sub3"),
                         "Default disk size of 50 GB at SSD speed")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image3"))
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image4"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line4"),
                         "Within seconds the machine is active.")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image5"))
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image6"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line5"),
                         "Unlike other clouds, OpenvCloud puts every virtual machine "
                         "behind a private firewall.")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line6"),
                         "To have access to your virtual machine you can create a VPN "
                         "connection (see other tutorials) or configure a")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line7"),
                         "port forwarding (means forward a port from your private firewall "
                         "to the port on your virtual machine).")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line8"),
                         "Here we will choose for the later option.")
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line9"),
                         "In order to configure the port forwarding, click on Port Forwards tab:")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image7"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line10"),
                         "Click the Add button, and specify that you want to forward port 3389:")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image8"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line11"),
                         "As a result you will see the below:")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image9"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line12"),
                         "On your Windows open")
        self.assertTrue(self.wait_element("knowledge_base_line5_tab_image10"))
        self.assertEqual(self.get_text("knowledge_base_line5_tab_line13"),
                         "Click connect and you should see your Windows")
        self.lg('%s ENDED' % self._testID)
    
    def test07_technical_tutorials_sixth_tab(self):
        """ PRTL-016
        *Test case for check user potal technical tutorials sixth tab.*

        **Test Scenario:**

        #. check all technical tutorials sixth tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)
        self.assertEqual(self.get_text("knowledge_base_header_label"),
                         "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line6_tab"),
                         "PPTP Connection To Space From Windows 10")
        self.click("knowledge_base_line6_tab")
        self.assertEqual(self.get_text("knowledge_base_line6_tab_header"),
                         "PPTP Connection to Cloud Space from Windows 10")
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line1"),
                         "Go to Settings:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image1"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line2"),
                         "In Settings go to Network -> Internet:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image2"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line3"),
                         "Click Add a VPN Connection:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image3"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line4"),
                         "Here you will need to specify the public IP address of the cloud space."
                         " For this you first need to go to the End User Portal:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image4"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line5"),
                         "In the End User Portal select Defense Shield:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image5"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line6"),
                         "Here click the Advanced Shield Configuration button:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image6"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line7"),
                         "Under IP | Addresses you will see the public IP address of your cloud "
                         "space:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image7"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line8"),
                         "Going back to configuration of the new VPN connection in Windows, "
                         "select the built-in VPN provider, specify a connection name and the "
                         "public IP address of your cloud space, in this case: 85.255.197.118.")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image8"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line9"),
                         "Hit the Save button and see the newly added VPN configuration listed:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image9"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line10"),
                         "When you click Connect you will be asked to specify for credentials, "
                         "for we first need to go back to the Advanced Defense Shield "
                         "Configuration, this time under PPP | Secrets:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image10"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line11"),
                         "Here click Add New and specify a username and password:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image11"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line12"),
                         "After click OK, use these credentials in the Sign in screen of Windows:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image12"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line13"),
                         "When you OK you should get connected:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image13"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line14"),
                         "Also in the Advanced Defense Shield Configuration under PPP | Active "
                         "Connections you will see that the connection was successful:")
        self.assertTrue(self.wait_element("knowledge_base_line6_tab_image14"))
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line15"),
                         "In this case you see that the Windows client did receive IP address "
                         "192.168.103.244.")
        self.assertEqual(self.get_text("knowledge_base_line6_tab_line16"),
                         "As a final test you will want to ping from your Windows machine another"
                         " (virtual) machine in the same cloud space.")
        self.lg('%s ENDED' % self._testID)

    def test08_technical_tutorials_seventh_tab(self):
        """ PRTL-017
        *Test case for check user potal technical tutorials seventh tab.*

        **Test Scenario:**

        #. check all technical tutorials seventh tab page elements, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.assertEqual(self.get_text("knowledge_base_header_label"), "Technical Tutorials")
        self.assertEqual(self.get_text("knowledge_base_line7_tab"), "Using the API")
        self.click("knowledge_base_line7_tab")
        self.assertEqual(self.get_text("knowledge_base_line7_tab_header"), "Using the API")

        self.lg('%s ENDED' % self._testID)
