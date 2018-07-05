from tests.ovc_master_hosted.Portal.framework.framework import Framework

class StatusTests(Framework):
    def setUp(self):
        super(StatusTests, self).setUp()
        self.Login.Login()
        self.StatusOverview.get_it()

    def test01_health_check(self):
        """ PRTL-029
        *Test case to make sure that the health check is working as expected*

        **Test Scenario:**
        #. go to status overview page
        #. press on "Run Healthcheck"
        #. verify expected behavior
        """
        health_check = self.StatusOverview.run_health_check()
        self.assertEqual(health_check, 'Scheduled healthcheck', 'Health check message: %s' % health_check)
