import time
import unittest
import uuid
from tests.ovc_master_hosted.Portal.framework.framework import Framework


class Write(Framework):
    def __init__(self, *args, **kwargs):
        super(Write, self).__init__(*args, **kwargs)

    def setUp(self):
        super(Write, self).setUp()
        self.Login.Login(cookies_login=True, portal='enduser')
        self.EUMachines.create_default_account_cloudspace(self.admin_username, self.account, self.cloudspace)
        self.assertTrue(self.EUMachines.end_user_create_virtual_machine(machine_name=self.machine_name))
        self.EUMachines.end_user_get_machine_page(machine_name=self.machine_name)
        self.EUMachines.end_user_get_machine_info(machine_name=self.machine_name)

    def test01_machine_stop_start_reboot_reset_pause_resume(self):
        """ PRTL-007
        *Test case for start/stop/reboot/reset/pause/resume machine.*

        **Test Scenario:**

        #. select running machine, should succeed
        #. stop machine, should succeed
        #. start machine, should succeed
        #. reboot machine, should succeed
        #. reset machine, should succeed
        #. reset machine using ctrl/alt/del button, should succeed
        #. pause machine, should succeed
        #. resume machine, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.lg('select running machine, should succeed')
        self.assertTrue(self.EUMachines.end_user_wait_machine("RUNNING"))


        self.lg('stop machine, should succeed')
        self.click("machine_stop")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.assertTrue(self.EUMachines.end_user_wait_machine("HALTED"))
        self.EUMachines.end_user_verify_machine_elements("HALTED")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("HALTED")
        self.EUMachines.end_user_verify_machine_elements("HALTED")

        self.lg('start machine, should succeed')
        self.click("machine_start")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_verify_machine_console("RUNNING")
        self.click("actions_tab")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")

        self.lg('reboot machine, should succeed')
        self.click("actions_tab")
        self.click("machine_reboot")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_verify_machine_console("RUNNING")
        self.click("actions_tab")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")

        self.lg('reset machine, should succeed')
        self.click("actions_tab")
        self.click("machine_reset")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_verify_machine_console("RUNNING")
        self.click("actions_tab")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")

        self.lg('reset machine using ctrl/alt/del button, should succeed')
        self.click("console_tab")
        self.EUMachines.end_user_verify_machine_console("RUNNING")
        self.click("send_ctrl/alt/del_button")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.click("actions_tab")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")

        self.lg('pause machine, should succeed')
        self.click("actions_tab")
        self.click("machine_pause")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_wait_machine("PAUSED")
        self.EUMachines.end_user_verify_machine_elements("PAUSED")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("PAUSED")
        self.EUMachines.end_user_verify_machine_elements("PAUSED")
        self.click("console_tab")
        self.EUMachines.end_user_verify_machine_console("PAUSED")

        self.lg('resume machine, should succeed')
        self.click("actions_tab")
        self.click("machine_resume")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("refresh_button")
        self.EUMachines.end_user_wait_machine("RUNNING")
        self.EUMachines.end_user_verify_machine_elements("RUNNING")
        self.click("console_tab")
        self.EUMachines.end_user_verify_machine_console("RUNNING")

        self.lg('%s ENDED' % self._testID)

    def test02_machine_create_rollback_delete_snapshot(self):
        """ PRTL-008
        *Test case for create snapshot machine.*

        **Test Scenario:**

        #. create new machine, should succeed
        #. create snapshot for a machine, should succeed
        #. rollback snapshot for a machine, should succeed
        #. delete snapshot for a machine, should succeed
        """
        self.lg('%s STARTED' % self._testID)

        self.lg('select running machine, should succeed')
        self.EUMachines.end_user_wait_machine("RUNNING")

        self.lg('create snapshot for a machine, should succeed')
        snapshot_name = str(uuid.uuid4())
        self.click("machine_take_snapshot")
        self.set_text("snapshot_name_textbox", snapshot_name)
        self.click("snapshot_ok_button")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.click("snapshot_tab")
        time.sleep(5)
        self.assertEqual(snapshot_name, self.get_text("first_snapshot_name"))

        self.lg('rollback snapshot for a machine, should succeed')
        self.click("actions_tab")
        self.lg('stop machine, should succeed')
        self.click("machine_stop")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.EUMachines.end_user_wait_machine("HALTED")
        self.EUMachines.end_user_verify_machine_elements("HALTED")
        self.click("snapshot_tab")
        self.click("first_snapshot_rollback")
        time.sleep(5)
        self.assertEqual(self.get_text("snapshot_confirm_message"),
                         "Snapshots newer then current snapshot will be removed.")
        self.click("snapshot_confirm_ok")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')
        self.click("first_snapshot_delete")
        time.sleep(5)
        self.assertEqual(self.get_text("snapshot_delete_message"),
                         "Are you sure you want to delete snapshot?")
        self.click("snapshot_delete_ok")
        self.wait_until_element_attribute_has_text('machine_operations_loading', 'style', 'display: none;')

        self.lg('%s ENDED' % self._testID)
