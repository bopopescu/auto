# -*- coding: utf-8 -*-
import ConfigParser


class RHIniParser(object):
    '''ini文件操作'''
    def __init__(self, file):
        self.file = file
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.file))

    def get_ini_info(self, section, option):
        return self.config.get(section, option)

    def set_ini_info(self, section, option, val):
        if section not in self.config.sections():
            self.config.add_section(section)
        self.config.set(section, option, val)
        self.config.write(open(self.file, "w+"))

    def del_ini_info(self, section, option=""):
        if option == "":
            self.config.remove_section(section)
        else:
            self.config.remove_option(section, option)
        self.config.write(open(self.file, "w+"))

    def get_ini_sections(self):
        return self.config.sections()


if __name__ == '__main__':
    # iniUWParser = RHIniParser("uw_form_task_assign_configuration.ini")
    file = r'D:\rh_auto_test\config\api\bank\msp\msp_para_configuration.ini'
    iniParser = RHIniParser(file)
    print eval(iniParser.get_ini_info("MODEL_URL", "MODEL_URL_DATA"))['RH_MSPSERVER']

