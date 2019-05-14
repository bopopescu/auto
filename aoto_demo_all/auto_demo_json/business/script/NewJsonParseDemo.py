# encoding=UTF-8

"""
http post get方式json格式参数请求处理

RIDE格式：
        说明：   "project01.majorIssue:getGrid",
                 "pageNum:=2",                           # 自定义替换接口参数
                u"msg:=请求成功",
        【project01：项目名；majorIssue:接口对应产品名(若没有，则为空); getGrid：接口名】
        三个一组为一个接口的处理；多个接口顺序写下去即可。
"""

import os
import re
import json
from time import sleep
import requests
from robot.api import logger
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from titanrun.common import Core
import titanrun.config.Settings as Settings
from titanrun.common.IniParser import RHIniParser
from titanrun.common.NewJsonBase import NewJsonBase

# 移除SSL认证，控制台输出InsecureRequestWarning。
urllib3.disable_warnings(InsecureRequestWarning)
session = requests.session()

class NewJsonParse(NewJsonBase):

    def new_jsonparse_pub(self, model="ride"):

        j = 0
        headers = {"Content-Type": 'application/json;charset=UTF-8'}
        token = ""
        if model == "ride":
            path = os.getcwd()
        else:
            path = os.path.abspath('..')
        Settings.CASE_GEN_DIC.clear()

        for i in xrange(self.api_len):      # 有多少个接口就循环跑多少次
            data_source_apis = self.data_source[i * 3].split(":")
            api = Core.rh_get_api_name(data_source_apis[1])
            interface_name = api

            # 再次循环对比接口和数据ini文件，取到接口数据所在的ini文件，支持多个ini文件存储数据
            for ini_name in self.ini_name_list:
                cur_path = os.path.join(path, "config", "api", self.api_name)
                ini_path = os.path.join(cur_path, ini_name)
                ini_data = RHIniParser(ini_path)
                # 循环读取ini文件，找到接口数据所在的ini文件
                default_data = self.get_ini_default_contant(ini_data)
                if api in default_data[0].keys() or api in default_data[4].keys():
                    break

            # 读取接口产品    [msp.01; msp; msp.03 ]
            product_name = self.get_productname(i)

            # 读取接口路径
            model_url = self.get_modelurl(ini_data, api, product_name)

            # 读取对应api接口的默认值
            ini_contant = self.get_ini_default_contant(ini_data, api, product_name)

            if ".db" not in api and ".dmldb" not in api:
                # 对应api接口的默认值，请求方式，出入参设置，正则表达式，特定返回值
                default_contant = ini_contant[0]
                request_method = ini_contant[1]
                in_para_dic = ini_contant[2]
                out_para_dic = ini_contant[2]
                default_re_set = ini_contant[3]

                if "||" in self.data_source[i * 3 + 1 - j]:  # 对rf的表格的取值，替换列的，注意替换项必须和url里面的一致
                    self.urlparam = self.data_source[i * 3 + 1 - j].split("||")[1]

                # 替换urlinput设置的变量--url
                interface_name = self.change_in_json_urldic(in_para_dic, self.dic_args, interface_name, self.urlparam)
                # 替换in out设置的变量--data
                self.change_in_json_dic(in_para_dic, self.dic_args, default_contant)

                # 替换设置的参数值
                self.change_para_json(default_contant,
                                      self.data_source[i * 3 + 1 - j].split("||")[0])  # data_source[1]    data_source[3]...

                # 走html处理的，或者是json 的get请求，不需要dumps
                if request_method == "get":
                    # #####==get请求参数要传dict，且dict中嵌套的list或者dict需要转换为str才能识别。=========#########
                    for k in default_contant:
                        if isinstance(default_contant[k], dict):
                            default_contant[k] = json.dumps(default_contant[k])
                        elif isinstance(default_contant[k], list):
                            default_contant[k] = str(default_contant[k])
                else:
                    # post请求参数为json，做dumps处理
                    default_contant = json.dumps(default_contant)

                # 处理需要登录中的Authorization
                token = self.dic_args.get("Authorization", "")

                # ============请求hearder组装START 如有需要，自行处理====================
                headers = dict(headers, **{"authorization": token})
                # iaas_cloud : token验证
                # if 'cloud_manage' in self.api_name or "auto_engine" in self.api_name:
                #     headers = {"Content-Type": 'application/json', 'X-Auth-Token': token.encode('utf-8')}
                # ============请求hearder组装END========================================

                print "请求接口:  " + self.version_url + model_url + interface_name
                print default_contant
                response_json = self.json_request(self.version_url + model_url + interface_name, default_contant, request_method, headers)
                print response_json[0]

                data = Core.rh_replace_data(self.data_source[i * 3 + 2 - j])
                for i in data:
                    res = self.rh_json_check_result(i, response_json[0])
                    if "[success]" not in res:
                        logger.error("%s failed:\n***********post data:\n%s\n***********response data:%s" % (
                            api, default_contant, response_json[0]))
                    self.Verify.should_contain(res, "[success]")
                # 获取正则表达式列表
                default_re = default_re_set.split(";")  # 存储特定返回值
                out = self.get_out_json_dic(out_para_dic, response_json[0], default_re)
                self.dic_args = self.get_new_dic(self.dic_args, out)
                print "%s:%s" % (api, self.dic_args)

    # ################################################################################################
    # ### 下面可以添加自己对于的项目需要特殊处理的方法。 自己调用即可 ###################################
    # 以下是example

    # # sq特殊处理---查询数据库值作为入参
    # def query_db_into_dicargs(self, sql, sid, key, dic_args, param=[]):
    #     sqlobj = DbImpl.connect_db(self.version, sid)
    #     dic_args[key] = sqlobj.fetchone_query(sql, param)[0]         # 取第一列值
    #     return dic_args
    #
    # # 替换登录请求参数
    # def change_login_dic(self, api_name, login_data, port="12021"):
    #     new_dict = {}
    #     for key in login_data:
    #         new_dict[key] = self.api_def_dic.get(api_name).get(key, "")
    #         try:
    #             if "toURL" in key:
    #                 new_dict[key] = self.change_url_port(new_dict[key], port)
    #                 # 替换对应登录参数
    #                 login_data[key] = new_dict[key]
    #         except Exception, e:
    #             raise Exception("error change, %s, %s" % (key, str(e)))
    #     return login_data

    # #################################################################################################


