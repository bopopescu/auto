# encoding=UTF-8

"""
JsonParse基类
"""

import re
import json
import types
import requests

from robot.api import logger

from business.conf import EnvSetting
from titanrun.common import Core
from titanrun.common.Core import get_var
from titanrun.common.DbOperate import RHOracle
from titanrun.common.IniParser import RHIniParser
from robot.libraries.BuiltIn import _Verify
from titanrun.common.Result import Result


class JsonBase(object):

    def __init__(self, data_source, version):
        self.dic_args = {}
        self.key_list = []              # 存储json接口返回的key值集合
        self.product_dict = {}          # 存储接口对应产品key值集合字典 {"1024": [xx,xxx]}
        self.result = Result()
        self.Verify = _Verify()
        self.upload_files = {}
        self.cur_path = ""
        self.ini_path = ""
        self.urlparam = ""
        self.default_data_dict = {}
        self.version = version
        self.data_source = data_source
        self.session = requests.session()

        # =========路径，产品，执行接口获取； eg：msp.apply.01;msp.apply:interface_a;interface_b ==========
        self.data_source_apis = self.data_source[0].split(":")  # 用 ：对datasource的第一个元素进行拆分
        self.apis = self.json_replace_data(self.data_source_apis[1])  # 入参是接口名   取出接口名
        self.interface_path_product = self.json_replace_data(self.data_source_apis[0])  # 入参是 msp.apply.01
        self.api_name = self.interface_path_product[0].split(".")[0]  # 取出了 msp
        self.api_len = len(self.apis)

        # ================获取接口属性=====================
        self.api_def_dic = EnvSetting.ENV_DEF_DIC
        self.db_def_dic = EnvSetting.ENV_DB_DIC
        self.version_dict = EnvSetting.VERSION
        self.env_pro_dic = self.api_def_dic.get(self.api_name)
        self.version_info = self.version_dict.get(version)
        self.version_port = self.version_info.get("port", self.env_pro_dic.get("port", ""))
        self.version_url = self.version_info.get("url", self.env_pro_dic.get("url", ""))
        self.version_uri = self.version_info.get("uri", self.env_pro_dic.get("uri", ""))
        self.version_url = self.concat_url()
        self.ini_name_list = self.env_pro_dic["api_ini_name"]

    # data 是 接口名 login;users/user_id/enable  该函数是取出每一个接口名
    def json_replace_data(self, data):
        data = str(data).strip().replace("\n", "").replace("”", "\"").replace("‘", "\'").replace("’", "\'").replace("；",";").decode("utf-8")
        if data.endswith(";"):
            data = data[:-1]
        return data.split(";")

    def concat_url(self):
        if self.version_uri != "":
            return "%s:%s/%s" % (self.version_url, self.version_port, self.version_uri)
        else:
            return "%s:%s" % (self.version_url, self.version_port)

    def get_productname(self, i):
        if len(self.interface_path_product) == 1:
            path_list = self.interface_path_product[0].split(".")
            if len(path_list) == 2:
                product_name = path_list[1]
            else:
                product_name = None
        else:
            path_list = self.interface_path_product[i].split(".")
            if len(path_list) == 2:
                product_name = path_list[1]
            else:
                product_name = None
        return product_name

    # 读取接口路径
    def get_modelurl(self, ini_data, api, product_name=None):
        model_url_data = json.loads(ini_data.get_ini_info("MODEL_URL", "MODEL_URL_DATA"))
        if len(model_url_data.keys()) == 1:
            model_url = model_url_data.values()[0]
        else:
            if product_name is None:
                model_url = model_url_data.get(api, "")
            else:
                model_url = model_url_data.get(api, "").get(product_name, "")
        return model_url

    # 替换入参json内容
    def change_para_json(self, json_cont, data):
        if data == "":
            return json_cont
        # try:
        #     t_js = json.loads(data)
        #     for ixe in t_js.keys():
        #         t_ixv = t_js.get(ixe)
        #         if isinstance(t_ixv, (basestring, dict, list)):
        #             t_ixv = get_var(t_ixv)
        #         json_cont[ixe] = t_ixv
        #     return json_cont
        # except:
        replace_data = self.json_replace_data(data)

        for data in replace_data:
            if "=" not in data:
                raise Exception("error format,not found =")
            try:
                if ":=" not in data:
                    raise Exception("error format")
                sval = get_var(data.split(":=")[1])
                name = data.split(":=")[0]
                # sval = sval.replace("'", "\"")
                # 对参数做num，str区分 数字：222222， str：'222222'
                if sval != "":
                    if sval.startswith("'") and sval.endswith("'"):
                        sval = str(sval[1:-1])
                    elif Core.is_numeric(sval):
                        if "." in sval:
                            sval = float(sval)
                        else:
                            sval = int(sval)
                    # 支持替换成空list或dict： a=[]; a={}
                    elif sval.startswith("[") or sval.startswith("{"):
                    # elif sval.replace(" ", "") == "[]" or sval.replace(" ", "") == "{}":
                        sval = Core.eval_str(sval)
                # 嵌套json替换
                obj = ""
                for i in name.split("."):
                    if Core.is_numeric(i):
                        obj = "%s[%s]" % (obj, i)
                    else:
                        obj = "%s['%s']" % (obj, i)
                # 对值为为bool, null的处理
                if sval == 'false':
                    sval = False
                elif sval == 'true':
                    sval = True
                elif sval == 'null' or sval == "":
                    sval = None
                scmd = "%s%s = sval" % ("json_cont", obj)
                exec scmd
            except Exception, e:
                raise Exception("error occur %s" % scmd)
        return json_cont

    # http json请求
    def json_request(self, url, json, method="post", headers={}, files={}):
        if method == "get":
            response = self.session.get(url, params=json, headers=headers, verify=False)
        elif method == "patch":
            response = self.session.patch(url, data=json, headers=headers, verify=False)
        elif method == "delete":
            response = self.session.delete(url, params=json, headers=headers, verify=False)
        elif method == "uploadfiles":
            response = self.session.post(url, data=json, files=files, headers=headers, verify=False)
        elif method == "put":
            response = self.session.put(url, data=json, headers=headers, verify=False)
        else:
            response = self.session.post(url, data=json, headers=headers, verify=False)

        return response.text, response.status_code, response.headers
        # return response.json()

    # 判断code
    def rh_get_rf_code(self, input):
        data = str(input).strip().replace("\n", "").replace("”", "\"").replace("‘", "\'").replace("’", "\'").replace(
            "；", ";")
        if data is None:
            raise Exception("error format,prepareResult is none.")

        pre_result = {}
        for ll in data.split(";"):
            ll02 = ll.split(":=")
            pre_result[ll02[0]] = ll02[1]

        status_code = pre_result.get('code')
        return status_code

    # 结果校验
    # 非json格式返回模板为:ResultInfoDesc:=自动核保通过(包含的message);
    # json返回模板为：error:=交易成功   其中实际值为："error":"交易成功"
    # 返回为list，模板为：1.aaa:=bbbb   或者 1:=bbbb
    def rh_json_check_result(self, input, response_json):
        data = str(input).strip().replace("\n", "").replace("”", "\"").replace("‘", "\'").replace("’", "\'").replace(
            "；", ";")
        if data is None:
            raise Exception("error format,prepareResult is none.")
        if input == "":
            return "[success]:response data contains %s." % data

        flag = False
        # eval()对特殊值处理
        # null = ""
        # true = True
        # false = False
        # 返回结果为list[]或者 json格式 比较
        if (response_json.startswith("[") or response_json.startswith("{")) and response_json not in ["[]", "{}"]:
            response_json = Core.eval_str(response_json)         # str转成list
            cmp_result = Core.rh_check_result(input, response_json)
            if "[success]"in cmp_result:
                flag = True
            else:
                return cmp_result
        # 返回结果为text
        else:
            except_message = data.split(":=")[1]
            if response_json.__contains__(except_message):
                flag = True
            else:
                return "[fail]:response data do not contains %s." % data
        if flag:
            return "[success]:response data contains %s." % data

    # 替换入参 in out设置的变量
    def change_in_json_dic(self, sdic, new_dic, json_cont):
        if new_dic != {}:
            if sdic.get("input", "") != "":
                for (sname, sval) in sdic.get("input", "").items():
                    try:
                        name = sname
                        value = new_dic[sval]
                        # 嵌套json替换
                        obj = ""
                        for i in name.split("."):
                            if Core.is_numeric(i):
                                obj = "%s[%s]" % (obj, i)
                            else:
                                obj = "%s['%s']" % (obj, i)
                        scmd = "%s%s = value" % ("json_cont", obj)
                        exec scmd
                        # json_cont[name] = value
                    except Exception, e:
                        raise Exception("error after change, %s" % scmd)

    # 替换url in out设置的变量
    def change_in_json_urldic(self, sdic, new_dic, url, data=""):
        # 替换url中设置替换的变量
        if data != "":
            replace_data = self.json_replace_data(data)
            for data in replace_data:
                url_name = data.split(":=")[0]
                url_param = data.split(":=")[1]
                url = url.replace(url_name, url_param)
        # 再替urlinput中需要替换的变量，若与设置需要替换的变量一致，则不会处理。
        elif new_dic != {}:
            if sdic.get("urlinput", "") != "":
                for (sname, sval) in sdic.get("urlinput", "").items():
                    try:
                        name = sname
                        vaule = new_dic[sval]
                        url = url.replace(str(name), str(vaule))
                        # url = url.replace(vaule, "82612502bac711e78e43d0a637ed6da3") # 用于修改非本用户用例
                    except Exception, e:
                        raise Exception("error after change, %s" % name)
        # print url
        return url

    # 更新token
    def change_in_token_dic(self, sdic, new_dic, token):
        if new_dic != {}:
            if sdic.get("headinput", "") != "":
                for (sname, sval) in sdic.get("headinput", "").items():
                    try:
                        name = sname
                        token = new_dic[sval]
                    except Exception, e:
                        raise Exception("error after change, %s" % name)
        return token

    # 获取接口返回的json内容，取对应字段存到sdic
    def get_out_json_dic(self, sdic, response_json, pattern):
        out = {}
        if sdic.get("output", "") != "":
            if 'jsonp' in response_json:
                response_json = response_json[response_json.find('{'):-2]
            i = -1
            if response_json.startswith("{") or response_json.startswith("["):
                # if response_json.startswith("{"):
                #     # 返回若为response.text 则需要转成json，若为response.json()，则不用
                #     response_json = json.loads(response_json)
                for (sname, sval) in sdic.get("output", "").items():
                    i += 1
                    try:
                        out[sname] = self.get_nestdict_value(sval, response_json)
                    except Exception, e:
                        logger.info("out arg %s not find" % sval)
            else:
                for (sname, sval) in sdic.get("output","").items():
                    i += 1
                    p = re.compile(pattern[i])
                    value = p.findall(response_json)
                    try:
                        out[sname] = value[0]                       # 取匹配到的第1个
                    except Exception,e:
                        logger.info("out arg %s not find" %sname)
        return out

    # 获取接口返回的response_header内容，取对应字段存到sdic
    def get_out_responseheader_dic(self, sdic, response_json):
        out = {}
        if sdic.get("header_output", "") != "":
            i = -1
            for (sname, sval) in sdic.get("header_output", "").items():
                i += 1
                try:
                    out[sname] = self.get_nestdict_value(sval, response_json)
                except Exception, e:
                    logger.info("out arg %s not find" % sval)
        return out

    def get_new_dic(self, new_out_dic, out):
        if out != {}:
            for (k, v) in out.items():
                new_out_dic[k] = v
        return new_out_dic

    # a=111&b=222 原生form表单格式转成dict
    def transfor_to_dict(self, data):
        listdata = data.split("&")
        properties = {}
        for line in listdata:
            if line.find("=") > 0:
                strs = line.replace("\n", "").replace("\t|\n", "").split("=")
                properties[strs[0]] = strs[1]
        return properties

    # 替换不同版本url, port方法
    def change_url_port(self, url, change_port, change_url=""):
        j = [m.start() for m in re.finditer(":", url)][1] + 1
        if "RH_" in url:
            k = [m.start() for m in re.finditer("/", url)][2]
            oraginal_port = url[j:k]
        else:
            oraginal_port = url[j:]
        oraginal_url = url[:j-1]
        url = url.replace(oraginal_port, change_port)
        if change_url != "":
            url = url.replace(oraginal_url, change_url)
        return url

    # json合并    嵌套的json取内值合并成一个
    # Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]} 输出： Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
    def get_format_dict(self, dictdata):
        for (k, v) in dictdata.items():
            if isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        new_dict = i.copy()
                        dictdata = dict(dictdata.items() + new_dict.items())
                dictdata.pop(k)
                if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                    return dictdata
                else:
                    return self.get_format_dict(dictdata)
            else:
                if isinstance(v, dict):
                    new_dict = v.copy()
                    dictdata.pop(k)
                    dictdata = dict(dictdata.items() + new_dict.items())
                    if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                        return dictdata
                    else:
                        return self.get_format_dict(dictdata)
        return dictdata

    # 获取字典中的objkey对应的值，适用于字典嵌套
    # dict:字典
    # objkey:目标key
    # default:找不到时返回的默认值
    # PS:若嵌套的json或者list中有key名称相同，则只能获取到第一个key的值，故只能取第一个key做对比
    def dict_get(self, dict, objkey, default=None):
        tmp = dict
        for k, v in tmp.items():
            if k == objkey:
                return v
            else:
                if type(v) is types.DictType:
                    ret = self.dict_get(v, objkey, default)
                    if ret is not default:
                        return ret
                elif type(v) is types.ListType:
                    for val in v:
                        ret = self.dict_get(val, objkey, default)
                        if ret is not default:
                            return ret
        return default

    # 获取复杂嵌套list，json对应的下标（key）值, 可以去到任意值
    # 格式：keytag： "2.a"      dict_data：[{"a": "111", "b": 222}, "bbbb", {"a": "555", "b": 222}]
    def get_nestdict_value(self, keytag, dict_data):
        if type(dict_data) not in [types.ListType, types.DictType]:     # 处理返回值为 "{}" ,"[]"情况
            # dict_data = json.loads(dict_data)
            dict_data = Core.eval_str(dict_data)  # 效果同上
        # 处理 "a": "[]" 情况
        dict_data = self.dict_handle(dict_data)
        sname = keytag.strip()
        obj = scmd = realval = ""
        for i in sname.split("."):
            if Core.is_numeric(i):
                obj = "%s[%s]" % (obj, i)
            else:
                if 'str(' in i:
                    i = i[i.find('(')+1:-1]
                obj = "%s['%s']" % (obj, i)
        scmd = "%s%s" % ("dict_data", obj)
        try:
            realval = eval(scmd)
        except:
            return "[Failed]:cmd change error,eval(%s)" % scmd
        return realval

    # 上传照片处理, 若需要上传多个附件，返回如下dict
    def upload_files_format(self, filedata, path):
        """
        :param filedata:        # 对于key必传，value非传的附件， 则传"" 即可。  eg: filedata = {"filename1": ""}
        :param path: 
        :return:         
            {
              "field1" : open("filePath1", "rb")),
              "field2" : open("filePath2", "rb")),
              "field3" : open("filePath3", "rb"))
            }
        """
        upload_files = {}
        for key in filedata.keys():
            if filedata[key] != "":
                filedata[key] = path + filedata[key]
            else:
                filedata[key] = ""
        for (k, v) in filedata.items():
            if v != "":
                vfile = open(v, 'rb')
                upload_files[k] = vfile
            else:
                upload_files[k] = ""
        return upload_files

    def get_dict_allkeys(self, dict_a):
        """
        多维/嵌套字典数据无限遍历，获取json返回结果的所有key值集合
        :param dict_a: 
        :return: key_list
        """
        if isinstance(dict_a, dict):  # 使用isinstance检测数据类型
            for x in range(len(dict_a)):
                temp_key = dict_a.keys()[x]
                temp_value = dict_a[temp_key]
                self.key_list.append(temp_key)
                self.get_dict_allkeys(temp_value)  # 自我调用实现无限遍历
        elif isinstance(dict_a, list):
            for k in dict_a:
                if isinstance(k, dict):
                    for x in range(len(k)):
                        temp_key = k.keys()[x]
                        temp_value = k[temp_key]
                        self.key_list.append(temp_key)
                        self.get_dict_allkeys(temp_value)
        return self.key_list

    # 两个list value值比较
    def check_list(self, list01, list02):
        """
        两个list value值比较, 若需要比较两个list值是否都互相包含，这替换参数顺序调用两次接口。
        :param list01: 
        :param list02: 
        :return: 
        """
        for x in list01:
            if x not in list02:
                return False
        return True

    def dict_handle(self, dict_data):
        """
        该方法处理json嵌套中，嵌套的json和list是str类型。则需要eval处理。 eg: {"a": "[]"}  --> {"a": []}
        :param dict_data: 
        :return: 
        """
        if type(dict_data) in [types.DictType]:
            for k, v in dict_data.items():
                if type(v) in [types.StringType, types.UnicodeType] and (str(v).startswith("[") or str(v).startswith("{")):
                    v1 = Core.eval_str(v)
                    dict_data[k] = v1
                else:
                    pass
        elif type(dict_data) in [types.ListType]:
            for l in dict_data:
                self.dict_handle(l)
        return dict_data

    # 判断ini文件有section才取值，没有默认返回{}
    def get_ini_value(self, ini_data, section_value, section_option):
        return str(ini_data.get_ini_info(section_value, section_option) if section_value in ini_data.get_ini_sections() else {})

    # 封装取ini默认数据方法
    def get_ini_default_contant(self, ini_data, api=None, product_name=None):
        # ini_data = RHIniParser(ini_path)
        if api is None and product_name is None:        # 该结果-为了循环遍历找到接口所在的ini
            default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA"))
            request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD"))
            in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT"))
            default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET"))
            sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC"))
            rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC"))
            return default_contant, request_method, in_out_para_dic, default_re_set, sql_list, rollback_sqllist
        elif product_name is None:
            if ".db" in api:
                sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC")).get(api, [])
                return sql_list
            elif ".dmldb" in api:
                rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC")).get(api, [])
                return rollback_sqllist
            else:
                default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA")).get(api, "")
                request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD")).get(api, "")
                in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT")).get(api, {})
                default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET")).get(api, "")
                result_jsonkeys_list = json.loads(self.get_ini_value(ini_data, "RESULT_JSONKEYS", "RESULT_JSONKEYS_DIC")).get(api, [])
                return default_contant, request_method, in_out_para_dic, default_re_set, result_jsonkeys_list
        else:
            if ".db" in api:
                sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC")).get(api, {}).get(product_name, [])
                return sql_list
            elif ".dmldb" in api:
                rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC")).get(api, {}).get(product_name, [])
                return rollback_sqllist
            else:
                default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA")).get(api, "").get(product_name, "")
                request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD")).get(api, {}).get(product_name, "")
                in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT")).get(api, {}).get(product_name, {})
                default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET")).get(api, {}).get(product_name, "")
                result_jsonkeys_list = json.loads(self.get_ini_value(ini_data, "RESULT_JSONKEYS", "RESULT_JSONKEYS_DIC")).get(api, {}).get(product_name, [])
                return default_contant, request_method, in_out_para_dic, default_re_set, result_jsonkeys_list

