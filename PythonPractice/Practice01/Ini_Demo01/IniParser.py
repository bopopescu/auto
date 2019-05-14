# -*- coding: utf-8 -*-
import ConfigParser
import json
import os


class RHIniParser(object):
    '''ini文件操作'''
    def __init__(self,file):
        self.file=file
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(self.file))
        
    def get_ini_info(self,section, option):
        return self.config.get(section,option)
    
    def set_ini_info(self,section,option, val):
        if section not in self.config.sections():
            self.config.add_section(section)
        self.config.set(section,option,val)
        self.config.write(open(self.file, "w+"))

    def del_ini_info(self, section, option=""):
        if option == "":
            self.config.remove_section(section)
        else:
            self.config.remove_option(section, option)
        self.config.write(open(self.file, "w+"))

    def get_ini_sections(self):
        return self.config.sections()


def get_ini_value(section_value, section_option):
    return str(ini_data.get_ini_info(section_value, section_option) if section_value in ini_data.get_ini_sections() else {})


if __name__ == '__main__':
    path = os.getcwd()
    file = path + "\%s" % "msp_para_configuration_fanhuaOut.ini"
    ini_data = RHIniParser(file)

    response_jsonkeys = ["aa", "cc"]

    product_dict = {}
    product_name = "owncheck"
    product_dict[product_name] = response_jsonkeys

    result_jsonkeys_dict = json.loads(ini_data.get_ini_info("RESULT_JSONKEYS", "RESULT_JSONKEYS_DIC"))
    print result_jsonkeys_dict
    result_jsonkeys_dict["login01"] = response_jsonkeys
    result_jsonkeys_dict["login03"] = product_dict
    # 转成str存储
    result_jsonkeys_dict = json.dumps(result_jsonkeys_dict)
    print result_jsonkeys_dict
    ini_data.set_ini_info("RESULT_JSONKEYS03", "RESULT_JSONKEYS_DIC", result_jsonkeys_dict)

    ini_sections = ini_data.get_ini_sections()
    print ini_sections

    RESULT_JSONKEYS_DIC = get_ini_value("RESULT_JSONKEYS04", "RESULT_JSONKEYS_DIC")
    print type(RESULT_JSONKEYS_DIC)
    print RESULT_JSONKEYS_DIC != "{}"



