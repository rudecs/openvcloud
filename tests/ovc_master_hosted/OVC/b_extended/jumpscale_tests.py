from JumpScale import j
from ....utils.utils import BaseTest


class JumpscaleTests(BaseTest):

    def test001_jumpscale_debug(self):
        """ OVC-021
        *Test case for checking if jumpscale in debug mode*

        **Test Scenario:**

        #. start new application
        #. check if jumpscale's debug mode is off, should succeed
        """

        # if we want to change debug value:
        # hrd = j.core.hrd.get('/opt/jumpscale7/hrd/system/system.hrd'); hrd.set('debug','0')
        self.lg('%s STARTED' % self._testID)

        self.lg('start new application')
        j.application.start('jsshell')

        self.lg('check if jumpscale\'s debug mode is off, should succeed ')
        self.assertEqual(j.application.debug, False)

        self.lg('%s ENDED' % self._testID)
