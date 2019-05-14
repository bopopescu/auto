#  -*- coding=UTF-8 -*-

"""
编写具体的webUi执行脚本， 即案例。
"""

import os
from robot.api import logger
from titanrun.common.Result import Result
from titanrun.fixtures.BaseCase import BaseCase
import titanrun.config.Settings as Settings
import time
from business.conf import EnvSetting
from selenium.common.exceptions import NoAlertPresentException



class Project01Common(BaseCase):
    def project01_login(self, val_data, elem_data):
        result = Result()
        try:
            time.sleep(Settings.TINY_TIMEOUT)
            # self.open(self.get_versionUrl() + val_data["url"])
            self.open_modelUrl(val_data["url"])
            self.maximize_window()
            self.update_text(elem_data["usr"], val_data["usr"])
            self.update_text(elem_data["pwd"], val_data["pwd"])
            self.update_text(elem_data["code"], val_data["code"])
            self.click(elem_data["btnSubmit"])
            result.flag = True
        except Exception, e:
            self.project01_save_error_and_screenshot(result, logger, e)
        finally:
            self.project01_replace_result_arg(result, val_data)
            return result

    def project01_getPolicyInfo(self, val_data, elem_data):
        '''
        功能描述: 资源平台 - 客户管理 - 保单查询
        '''
        result = Result()
        try:
            time.sleep(Settings.TINY_TIMEOUT)
            # self.open(self.get_versionUrl() + val_data["clientList_url"])
            self.open_modelUrl(val_data["clientList_url"])
            self.click(elem_data["btnGetpolicy"])
            self.update_text(elem_data["policyNo"], val_data["policyNo"])
            self.click(elem_data["btnClick"])
            result.flag = True
            # 若有需要存储的返回值，则需要赋值到val_data --> val_data["key"] = result_data
            # val_data["key"] = result_data
        except Exception, e:
            self.project01_save_error_and_screenshot(result, logger, e)
        finally:
            self.project01_replace_result_arg(result, val_data)
            return result

    def project01_clientList(self, val_data, elem_data):
        '''
        功能描述: 客户管理-承保客户查询
        '''
        result = Result()
        try:
            time.sleep(Settings.TINY_TIMEOUT)
            # self.open(self.get_versionUrl() + val_data["request_url"])
            self.open_modelUrl(val_data["request_url"])
            self.click(elem_data["clientListLink"])

            self.wait_for_element(elem_data["queryButton"])
            # 客户姓名查询
            self.update_text(elem_data["clientName"], val_data["clientName"])
            self.click(elem_data["queryButton"])

            # 客户号查询
            self.driver.find_element_by_xpath(elem_data["clientName"]).clear()
            self.update_text(elem_data["clientNo"], val_data["clientNo"])
            self.click(elem_data["queryButton"])

            # 身份证号查询
            self.driver.find_element_by_css_selector(elem_data["clientNo"]).clear()
            self.pick_select_option_by_text(elem_data["idType"], val_data["idType"])
            self.update_text(elem_data["idNo"], val_data["idNo"])
            self.click(elem_data["queryButton"])

            # 全条件查询
            self.driver.find_element_by_css_selector(elem_data["idNo"]).clear()
            self.update_text(elem_data["clientName"], val_data["clientName"])
            self.update_text(elem_data["clientNo"], val_data["clientNo"])
            self.pick_select_option_by_text(elem_data["idType"], val_data["idType"])
            self.update_text(elem_data["idNo"], val_data["idNo"])
            self.click(elem_data["queryButton"])
            # 查看详细内容
            self.click(elem_data["queryDetail"])
            time.sleep(1)

            # 窗口切换
            self.switch_to_other_window()

            # 结果检查
            result.flag = self.result_msg_check(elem_data, val_data, "infoDetail")

        except Exception, e:
            self.project01_save_error_and_screenshot(result, logger, e)
        finally:
            self.project01_replace_result_arg(result, val_data)
            return result

    def project01_logout(self, val_data, elem_data):
        result = Result()
        try:
            self.click(elem_data["btnLogout"])
            self.find_btn_and_click(elem_data["btnTitle"], elem_data["btnYes"])
            result.flag = True
        except Exception, e:
            self.project01_save_error_and_screenshot(result, logger, e)
        finally:
            self.project01_replace_result_arg(result, val_data)
            return result

    # 内部调用函数    --若有需要存储的值，则自己添加
    def project01_replace_result_arg(self, result, val_data):
        """将新值val_data中的arg替换到result.arg中去"""
        if result.flag:
            if val_data.has_key("policyNo") and val_data["policyNo"] != '':
                result.arg["policyNo"] = val_data["policyNo"]
            if val_data.has_key("posNo") and val_data["posNo"] != '':
                result.arg["posNo"] = val_data["posNo"]
        else:
            result.arg["policyNo"] = result.arg["posNo"] = ''

    def project01_save_error_and_screenshot(self, result, logger, e):
        try:
            result.flag = False
            result.msg = str(e)
            logger.error(str(e))
            curtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            filename = "project01_" + curtime + ".png"
            folder = "screenshot"
            self.save_screenshot(filename, folder)
        except Exception, e:
            logger.error(str(e))
        return result

    # ==================================== 下面可以添加一些自己需要特出处理的方法 ========================================
    # 结果校验
    def result_msg_check(self, elem_data, val_data, elem_key):
        result = Result()
        if self.find_element(elem_data[elem_key]) is not None:
            insure_result = self.get_text(elem_data[elem_key])
            if val_data[elem_key] in insure_result:
                logger.info("成功-结果： %s" % insure_result)
                result.flag = True
            else:
                logger.info("失败原因： %s" % insure_result)
                result.flag = False
        else:
            al01 = self.driver.switch_to_alert()
            logger.info("失败原因： %s" % al01.text)
            result.flag = False
        return result.flag

    # 两个窗口间切换窗口
    def switch_to_other_window(self):
        now_handle = self.driver.current_window_handle
        handles = self.driver.window_handles
        for handle in handles:
            if handle != now_handle:
                self.driver.switch_to_window(handle)

    # 判断是否有alert弹窗
    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException, e:
            return False
        return True

    # 获取对应版本的web_url            # 该出为特殊处理把取项目的url_web写成方法，方便每个案例直接调用
    def get_versionUrl(self):
        return EnvSetting.VERSION.get(self.version, {}).get("url_web", EnvSetting.ENV_DEF_DIC["project01"]["url_web"])

    # 打开对应模块url
    def open_modelUrl(self, modelurl):
        self.open(self.get_versionUrl() + modelurl)

        # ==================================== 添加一些自己需要特出处理的方法-END ===========================================


if __name__ == '__main__':
    file_path = os.path.abspath("..\..")
    files = r"%s\config\file\1.jpg" % file_path
    print files
