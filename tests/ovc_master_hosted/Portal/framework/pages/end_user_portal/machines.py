import uuid
from random import randint
import time

class machines():
    def __init__(self, framework):
        self.framework = framework

    def create_default_account_cloudspace(self, user, account, cloudspace):
        self.framework.lg('create new account')
        self.framework.Accounts.create_new_account(account, user+"@itsyouonline")
        self.framework.lg('create new cloudspace')
        self.framework.CloudSpaces.create_cloud_space(account, cloudspace)
        self.framework.EUHome.get_it()

    def delete_default_account_cloudspace(self, account, cloudspace):
        self.framework.lg('delete Cloudspace')
        self.framework.assertTrue(self.framework.CloudSpaces.delete_cloudspace(cloudspace))
        self.framework.lg('delete account')
        self.framework.Accounts.delete_account(account)

    def end_user_create_virtual_machine(self, image_name="Ubuntu 16.04 x64", machine_name=''):

        self.framework.RightNavigationMenu.Machines.home()
        self.framework.click("create_machine_button")
        time.sleep(2)

        machine_name = machine_name or str(uuid.uuid4()).replace('-', '')[0:10]
        machine_description = str(uuid.uuid4()).replace('-', '')[0:10]

        self.framework.lg("Create a machine name: %s image:%s" % (machine_name, image_name))
        self.framework.set_text("machine_name", machine_name)
        self.framework.set_text("machine_description_", machine_description)

        if 'Windows' in image_name:
            self.framework.click('windows')
            time.sleep(2)

        elif "Ubuntu" in image_name:
            self.framework.click('linux')
            time.sleep(2)

        self.framework.click(image_name)
        time.sleep(2)

        num_available_packages = len(self.framework.find_element('packages').find_elements_by_tag_name('li'))
        randome_package = randint(1, num_available_packages)
        self.framework.click_item("package", [randome_package])
        time.sleep(2)

        num_available_disk_sizes = len(self.framework.find_element('disk_sizes').find_elements_by_tag_name('button'))
        random_disk_size = randint(1, num_available_disk_sizes)
        self.framework.click_item("disk_size", [random_disk_size])
        time.sleep(2)

        self.framework.click("create_machine")
        time.sleep(2)
        for temp in range(50):
            if "console" in self.framework.get_url():
                time.sleep(1)
                break
            else:
                time.sleep(1)
        else:
            self.framework.lg("FAIL : %s Machine can't create in 30 sec" % machine_name)
            return False


        time.sleep(5)
        for temp in range(50):
            if self.framework.get_text("machine_ipaddress") != "Undefined":
                self.framework.lg(' machine is created')
                return True
            else:
                self.framework.click('refresh_button')
                time.sleep(2)
        else:
            self.framework.lg("FAIL : %s Machine isn't RUNNING" % machine_name)
            return False


    def end_user_get_machine_page(self, machine_name=''):
        machine_name = machine_name
        self.framework.click("machines_button")
        time.sleep(2)
        if self.framework.check_element_is_exist("end_user_machine_table"):
            machine_table = self.framework.find_element("end_user_machine_table")
            machine_table_rows = machine_table.find_elements_by_class_name("ng-scope")

            for row in machine_table_rows:
                items = row.find_elements_by_class_name("ng-binding")
                if machine_name == items[1].text:
                    self.framework.machine = items[1]
                    self.framework.machine_memory = items[3].text
                    self.framework.machine_cpu = items[4].text
                    self.framework.machine_storage = items[5].text
                    row.find_element_by_link_text(machine_name).click()
                    for _ in range(3):
                        if not self.framework.check_element_is_exist("end_user_machine_name"):
                            time.sleep(1)
                        else:
                            break
                    self.framework.assertIn(machine_name, self.framework.get_text("end_user_machine_name"),
                                            "can't find %s machine in the table" % machine_name)
                    break
            else:
                self.framework.fail("can't find %s machine in the table" % machine_name)
                return False

    def end_user_get_machine_info(self, machine_name=''):
        self.framework.assertIn(machine_name, self.framework.get_text("end_user_machine_name"),
                                                                      "can't find %s machine in the table" % machine_name)

        if self.framework.check_element_is_exist("machine_description"):
            self.framework.machine_description = self.framework.get_text("machine_description")
        else:
            self.framework.machine_description = ''
        self.framework.machine_status = self.framework.get_text("machine_status")
        self.framework.machine_ipaddress = self.framework.get_text("machine_ipaddress")
        self.framework.machine_osimage = self.framework.get_text("machine_osimage")
        self.framework.machine_credentials = self.framework.get_text("machine_credentials")

    def end_user_wait_machine(self, status):
        for _ in range(30):
            if self.framework.get_text("machine_status") == status:
                return True
            else:
                time.sleep(1)
        else:
            return False

    def end_user_verify_machine_elements(self, status):
        if self.framework.machine_description:
            self.framework.assertEqual(self.framework.machine_description,
                                       self.framework.get_text("machine_description"))
        self.framework.assertEqual(status, self.framework.get_text("machine_status"))
        self.framework.assertEqual(self.framework.machine_ipaddress, self.framework.get_text("machine_ipaddress"))
        self.framework.assertEqual(self.framework.machine_osimage, self.framework.get_text("machine_osimage"))
        self.framework.assertEqual(self.framework.machine_credentials, self.framework.get_text("machine_credentials"))
        self.framework.assertEqual(self.framework.machine_cpu, self.framework.get_text("machine_cpu"))
        self.framework.assertEqual(self.framework.machine_memory, self.framework.get_text("machine_memory"))
        self.framework.assertEqual(self.framework.machine_storage, self.framework.get_text("machine_storage"))

    def end_user_verify_machine_console(self, status):
        if status == 'RUNNING':
            self.framework.assertEqual(self.framework.get_text("console_message_running"),
                                       "Click the console screen or use the control buttons below to "
                                       "get access to the screen. In case of a black screen, hit any key "
                                       "to disable the screen saving mode of your virtual machine.")
            self.framework.assertEqual(self.framework.get_text("console_ipaddress"), self.framework.machine_ipaddress)
            self.framework.assertTrue(self.framework.find_element("capture_button").is_displayed())
            self.framework.assertTrue(self.framework.find_element("send_ctrl/alt/del_button").is_displayed())
        else:
            self.framework.assertEqual(self.framework.get_text("console_message_halted"),
                                       "A machine must be started to access the console!")
            self.framework.assertFalse(self.framework.find_element("capture_button").is_displayed())
            self.framework.assertFalse(self.framework.find_element("send_ctrl/alt/del_button").is_displayed())

    def end_user_start_machine(self, machine):
        self.framework.click_link(machine)
        if self.framework.get_text("machine_status") != "RUNNING":
            self.framework.click("machine_start")
            time.sleep(30)
            self.framework.click("actions_tab")
            self.framework.click("refresh_button")

    def end_user_delete_virtual_machine(self, virtual_machine):
        self.framework.lg('Open end user home page')
        self.framework.RightNavigationMenu.Machines.home()

        if self.framework.check_element_is_exist("machines_button"):
            self.framework.lg(' Start creation of machine')
            self.framework.click("machines_button")

            if self.framework.check_element_is_exist("end_user_machine_table"):
                self.framework.lg('Open the machine page to destroy it')
                machine_table = self.framework.find_element("end_user_machine_table")
                machine_table_rows = machine_table.find_elements_by_class_name("ng-scope")

                for counter in range(len(machine_table_rows)):
                    machine_name_xpath = self.framework.elements["end_user_machine_name_table"][1] % (counter + 1)
                    machine_name = self.framework.driver.find_element_by_xpath(machine_name_xpath)
                    if virtual_machine == machine_name.text:
                        machine_name.click()
                        break
                else:
                    self.framework.lg("can't find %s machine in the table" % virtual_machine)
                    return False

                self.framework.lg("Destroy the machine")
                self.framework.click("destroy_machine")
                self.framework.click("destroy_machine_confirm")
                time.sleep(10)
                if self.framework.get_text("machine_list") == "Machines" or self.framework.element_is_displayed('no_machines_message'):
                    return True
                else:
                    self.framework.lg("FAIL : Can't delete %s machine" % virtual_machine)
                    return False
            else:
                self.framework.lg("There is no machines")
                return False
        else:
            self.framework.lg("FAIL : Machine button isn't exist for this user")
            return False

    def end_user_choose_account(self, account=''):
        account = account or self.framework.account
        self.framework.lg('Open end user home page')
        self.framework.get_page(self.framework.environment_url)
        if self.framework.check_element_is_exist("end_user_selected_account"):
            print(account, self.framework.get_text("end_user_selected_account"))
            if account not in self.framework.get_text("end_user_selected_account"):
                accounts_xpath = self.framework.elements["end_user_accounts_list"][1]
                for temp in range(100):
                    try:
                        account_item = self.framework.driver.find_element_by_xpath(accounts_xpath % temp)
                    except:
                        self.framework.lg("Can't choose %s account from the end user" % account)
                        return False
                    else:
                        if account in account_item.text:
                            account_item.click()
                            cloud_space_xpath = self.framework.elements["end_user_cloud_space"][1] % account
                            self.framework.driver.find_element_by_xpath(cloud_space_xpath).click()
                            return True
            else:
                return True
        else:
            self.framework.lg("This user doesn't has any account")
            return False
