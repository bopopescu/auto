# encoding=UTF-8

"""
html 默认form表单方式请求处理

RIDE格式：
        说明：msp:interface_a
              msp.1005:interface_a
            【msp：项目名；1005:接口对应产品名(若没有，则为空);interface_a：接口名】
        一个接口只有一个默认参数情况：msp.apply:interface_a
        一个接口有多个默认参数情况：msp.01:interface_a
        多个接口组合调用（只要有一个接口需要写产品，则所有接口都需三项写全）：msp.01;msp.02:interface_a;interface_b
"""

import platform
import os
import json
import re
from time import sleep
import requests
from robot.api import logger
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict

from titanrun.common import Core
import titanrun.config.Settings as Settings
from titanrun.common.IniParser import RHIniParser
from titanrun.common.HtmlBase import HtmlBase
from titanrun.common.JsonBase import JsonBase
from titanrun.common.DbOperate import RHOracle
from business.conf import EnvSetting
from titanrun.common import DbImpl


# 移除SSL认证，控制台输出InsecureRequestWarning。
urllib3.disable_warnings(InsecureRequestWarning)
session = requests.session()
# 兼容windows和linux分隔符处理
fileSep = os.path.sep


class HtmlParse(HtmlBase):

    def htmlparse_pub(self, model="ride"):

        j = 0
        ini_data = ""
        # ============请求头等初始化信息（需要的则自行添加）===========
        headers = {}
        token = ""
        cookies = ""
        upload_files = ""
        handler_version_url = ""
        # 此处为表单上传附件接口处理，若无，则为空 []
        list_upload = ["uploadImage"]
        # =====================END=============================================================================
        # =====上一层目录-实现类调用==============
        if model == "ride":
            path = os.getcwd()
        else:
            path = os.path.abspath('..')

        # ========URL固定不变的，每个版本替换port处理============================
        self.version_url = self.change_url_port(self.version_url, self.version_port)

        # 执行案例前清空CASE_GEN_DIC
        '''PS：经验证不能使用Settings.CASE_GEN_DIC = {}，否则后续其他用例调用值一直保持第一次的，
        原因分析?: Settings.CASE_GEN_DIC = {} 对CASE_GEN_DIC的引用改变了，CASE_GEN_DIC的值未改变;clear则清空该引用中的值
        '''
        Settings.CASE_GEN_DIC.clear()

        for i in xrange(self.api_len):                               # (0,2)
            interface_name = self.apis[i]
            api = Core.rh_get_api_name(self.apis[i])

            # 再次循环对比接口和数据ini文件，取到接口数据所在的ini文件，支持多个ini文件存储数据
            for ini_name in self.ini_name_list:
                cur_path = r'%s%sconfig%sapi%s%s' % (path, fileSep, fileSep, fileSep, self.api_name)
                ini_path = r"%s%s%s" % (cur_path, fileSep, ini_name)
                ini_data = RHIniParser(ini_path)
                # 循环读取ini文件，找到接口数据所在的ini文件
                default_data = self.get_ini_default_contant(ini_data)
                if self.apis[i] in default_data[0].keys() or self.apis[i] in default_data[4].keys() or self.apis[i] in default_data[5].keys():
                    break

            # 读取接口产品    [msp.01; msp; msp.03 ]
            product_name = self.get_productname(i)

            model_url = self.get_modelurl(ini_data, api)

            # model_url = self.get_modelurl(ini_data, api, product_name)

            # 读取对应api接口的默认值
            ini_contant = self.get_ini_default_contant(ini_data, api, product_name)

            if ".db" not in api and ".dmldb" not in api:
                # 读取对应api接口的默认值，请求方式，出入参设置，正则表达式，特定返回值
                default_contant = ini_contant[0]
                request_method = ini_contant[1]
                in_para_dic = ini_contant[2]
                out_para_dic = ini_contant[2]
                default_re_set = ini_contant[3]

                # 原始数据转成dict, 若原本为dict，则直接返回
                default_contant = self.transfor_to_dict(default_contant)

                if "||" in self.data_source[i * 2 + 1 - j]:  # 对rf的表格的取值，替换列的，注意替换项必须和url里面的一致
                    self.urlparam = self.data_source[i * 2 + 1 - j].split("||")[1]
                # 替换urlinput设置的变量--url
                interface_name = self.change_in_html_urldic(in_para_dic, self.dic_args, interface_name, self.urlparam)

                # ============ 一些需要自己特殊处理的接口方法可以执行书写 ================================================
                # sq特殊处理
                if interface_name in ["getVerifyCode.do", "Login.sso"]:
                    handler_version_url = self.version_url.replace(r"/"+self.version_uri, "")
                    self.version_url = handler_version_url
                # 同一流程里需要还原
                else:
                    self.version_url = handler_version_url + r"/"+self.version_uri

                # sq特殊处理    查询数据库存储对应的值到dic_args， 通过input引用
                # if interface_name in ["staffBindWechat", "salesmanBindWechat", "agentBind", "staffBind"]:
                #     sleep(5)    # 确保数据已经入库
                #     self.dic_args = self.query_db_into_dicargs(EnvSetting.ENV_SQL_DIC.get(interface_name, ""), "tablet", "checkCode", self.dic_args, str(default_contant["phoneNo"]).split())
                # # sq特殊处理    短信发送间隔必须大于30s
                # if interface_name in ["commonPayApply.do"]:
                #     sleep(30)
                # ============ 一些需要自己特殊处理的接口方法可以执行书写-END ============================================

                # 替换in out设置的变量--data
                self.change_in_html_dic(in_para_dic, self.dic_args, default_contant)
                # 替换设置的参数值
                self.change_para_html(default_contant, self.data_source[i * 2 + 1 - j].split("||")[0])  # data_source[1]    data_source[3]...

                # ============请求hearder组装 如有需要，自行处理====================
                token = self.dic_args.get("token", "")
                # header需要放token的处理
                if ("newWechat" in model_url) and "updatePwd" not in api:
                    headers = dict(headers, **{"authorization": "Bearer " + token})

                '''上传照片接口单独处理获取照片'''
                if api in list_upload:
                    if "Windows" in platform.system():
                        local_files = json.loads(ini_data.get_ini_info("UPLOAD", "UPLOAD_DEFAULT_FILES"))[api].get("windows", {})
                    else:       # 不是Windows 就默认是Linux
                        local_files = json.loads(ini_data.get_ini_info("UPLOAD", "UPLOAD_DEFAULT_FILES"))[api].get("linux", {})
                    upload_files = self.upload_files_format(local_files, path)

                print "请求接口:  " + self.version_url + model_url + interface_name
                # print default_contant

                # 发送请求
                response_html = self.html_request(self.version_url+model_url+interface_name, default_contant, cookies, upload_files, request_method, headers)
                print response_html

                data = Core.rh_replace_data(self.data_source[i * 2 + 2-j])
                for i in data:
                    res = self.rh_html_check_result(i, response_html)
                    if "[success]" not in res:
                        logger.error("%s failed:\n***********post data:\n%s\n***********response data:%s" % (api, default_contant,response_html))
                    self.Verify.should_contain(res, "[success]")
                # 获取正则表达式列表
                default_re = default_re_set.split(";")
                # 存储特定返回值
                out = self.get_out_html_dic(out_para_dic, response_html, default_re)
                self.dic_args = self.get_new_dic(self.dic_args, out)
                print "%s:%s" %(api, self.dic_args)

    # ======================== 以下可以增加自己需要特殊处理的方法 =======================================================
    # 截取-获取登录地址 域名+端口
    def get_login_url(self, url):
        if "RH_" in url:
            k = [m.start() for m in re.finditer("/", url)][2]
            url = url[0:k]
        return url

    # 替换登录请求参数--MSP登录修改参数中端口号特殊处理
    def change_login_dic(self, api_name, login_data, port="di1"):
        new_dict = {}
        for key in login_data:
            new_dict[key] = self.api_def_dic.get(api_name).get(key, "")
            try:
                if "toURL" in key:
                    new_dict[key] = self.change_url_port(new_dict[key], port)
                    # 替换对应登录参数
                    login_data[key] = new_dict[key]     # 放在if中，只做toURL的替换，不做username，password的替换，兼容考勤管理系统用不同的用户登录
            except Exception, e:
                raise Exception("error change, %s, %s" % (key, str(e)))
        return login_data

    # sq特殊处理---查询数据库值作为入参
    def query_db_into_dicargs(self, sql, sid, key, dic_args, param=[]):
        sqlobj = DbImpl.connect_db(self.version, sid)
        dic_args[key] = sqlobj.fetchone_query(sql, param)[0]         # 取第一列值
        return dic_args
    # ======================== 以下可以增加自己需要特殊处理的方法--END ==================================================
