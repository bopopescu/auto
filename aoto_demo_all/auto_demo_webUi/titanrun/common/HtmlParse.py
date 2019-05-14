# encoding=UTF-8

"""
html 默认form表单方式请求处理

RIDE格式：
        说明：msp.apply:interface_a
              msp.apply.1005:interface_a
            【msp：项目名；apply：模块-路径名；1005:接口对应产品名(若没有，则为空);interface_a：接口名】
        一个接口只有一个默认参数情况：msp.apply:interface_a
        一个接口有多个默认参数情况：msp.apply.01:interface_a
        多个接口组合调用（只要有一个接口需要写产品，则所有接口都需三项写全）：msp.apply.01;msp.apply:interface_a;interface_b
"""

import os
import re
import json
import types
from time import sleep
import requests
from robot.api import logger
from robot.libraries.BuiltIn import _Verify
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict

from business.conf import EnvSetting
from titanrun.common import Core
from titanrun.common.Core import get_var
from titanrun.common.DbOperate import RHOracle
from Result import Result
import titanrun.config.Settings as Settings
from titanrun.common.IniParser import RHIniParser


# 移除SSL认证，控制台输出InsecureRequestWarning。
urllib3.disable_warnings(InsecureRequestWarning)
session = requests.session()


def html_model_pub(data_source, version="1221", model="ride"):
    dic_args = {}
    result = Result()
    Verify = _Verify()
    upload_files = {}
    ini_path = ""
    urlparam = ""
    default_data_dict = {}
    # ============请求头信息（需要的则自行添加）===========
    # 手动添加一下header防反爬 --ChunkedEncodingError: ("Connection broken: error(10054, '')", error(10054, ''))报错
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}

    headers_wechat = {"Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602."}
    authorization = ""
    # ===================================================
    j = 0
    # return
    if model == "ride":
        path = os.path.abspath('.')
    else:
        path = os.path.abspath('../..')

    # =============路径，产品，执行接口获取;eg：msp.apply.01;msp.apply:interface_a;interface_b=============
    data_source_apis = data_source[0].split(":")  # 用 ：对datasource的第一个元素进行拆分
    apis = html_replace_data(data_source_apis[1])  # 入参是接口名   取出接口名
    interface_path_product = html_replace_data(data_source_apis[0])  # 入参是 msp.apply.01
    api_name = interface_path_product[0].split(".")[0]  # 取出了 msp
    api_len = len(apis)

    # ================获取接口属性=====================
    api_def_dic = EnvSetting.ENV_DEF_DIC
    version_dict = EnvSetting.VERSION
    version_info = version_dict.get(version)
    version_port = version_info["port"]
    version_url = version_info.get("url", "")
    env_pro_dic = api_def_dic.get(api_name)
    main_url = env_pro_dic["url"]
    # ========获取url截取点==========
    main_url = change_url_port(main_url, version_port, version_url)
    login_url = get_login_url(main_url)
    # ==============================
    ini_name_list = env_pro_dic["api_ini_name"]
    # ====循环对比接口和数据ini文件，取到第一个接口数据所在的ini文件，主要是为了先获取登录参数，看第一个接口是否需要登录
    for ini_name in ini_name_list:
        cur_path = r'%s\config\api\%s' % (path, api_name)
        ini_path = r"%s\%s" % (cur_path, ini_name)
        # 循环读取ini文件，找到接口数据所在的ini文件
        default_data_dict = get_ini_default_contant(ini_path, None, None)[0]
        if apis[0] in default_data_dict.keys():
            break
    # 执行案例前清空CASE_GEN_DIC
    '''PS：经验证不能使用Settings.CASE_GEN_DIC = {}，否则后续其他用例调用值一直保持第一次的，
    原因分析?: Settings.CASE_GEN_DIC = {} 对CASE_GEN_DIC的引用改变了，CASE_GEN_DIC的值未改变;clear则清空该引用中的值
    '''
    Settings.CASE_GEN_DIC.clear()
    '''获取cookies (调试接口用)=====有登陆接口传{}即可=============================================='''
    # default_cookies = RHIniParser(ini_path).get_ini_info("COOKIES", "SET_COOKIES")
    # cookies = str_to_dict(default_cookies, ";", "=")
    cookies = {}
    '''==========================================================================================='''
    '''========================判断系统是否需要登录=================================================='''
    login_sign = RHIniParser(ini_path).get_ini_info("IS_LOGIN", "LOGIN_SIGN")
    if login_sign is "Y":
        # 获取登录请求地址
        # 利用有序OrderedDict 有序读取url（有些登录需要验证码，需现请求获取验证码接口，防止验证码过期）
        login_url_dict = json.loads(RHIniParser(ini_path).get_ini_info("IS_LOGIN", "LOGIN_URL"),
                                    object_pairs_hook=OrderedDict)
        for url in login_url_dict.keys():
            ini_contant = get_ini_default_contant(ini_path, url, None)
            request_method = ini_contant[1]
            in_para_dic = ini_contant[2]
            out_para_dic = ini_contant[2]
            default_re_set = ini_contant[3]
            post_data = transfor_to_dict(login_url_dict[url])
            # 若为登录请求接口，替换对应参数兼容各个版本
            change_login_dic(api_name, post_data, version_port)
            # 替换urlinput设置的变量--url
            url = change_in_html_urldic(in_para_dic, dic_args, url, urlparam)
            # 替换in out设置的变量--data
            change_in_html_dic(in_para_dic, dic_args, post_data)
            response_html = html_request(login_url + url, post_data, request_method)
            # 获取正则表达式列表
            default_re = default_re_set.split(";")  # 存储特定返回值
            out = get_out_html_dic(out_para_dic, response_html, default_re)
            dic_args = get_new_dic(dic_args, out)
    '''==========================================================================================='''
    for i in xrange(api_len):                               # (0,2)
        interface_name = apis[i]
        api = Core.rh_get_api_name(apis[i])

        # 再次循环对比接口和数据ini文件，取到接口数据所在的ini文件，支持多个ini文件存储数据
        for ini_name in ini_name_list:
            cur_path = r'%s\config\api\%s' % (path, api_name)
            ini_path = r"%s\%s" % (cur_path, ini_name)
            # 循环读取ini文件，找到接口数据所在的ini文件
            default_data_dict = get_ini_default_contant(ini_path, None, None)[0]
            default_dbdata_dict = get_ini_default_contant(ini_path, None, None)[4]
            if apis[i] in default_data_dict.keys() or apis[i] in default_dbdata_dict.keys():
                break

        # 读取接口路径, 产品    [msp.apply.01; msp.apply; msp.tools.03 ]
        if len(interface_path_product) == 1:
            path_list = interface_path_product[0].split(".")
            model = path_list[1]
            if len(path_list) == 3:
                product_name = path_list[2]
            else:
                product_name = None
        else:
            path_list = interface_path_product[i].split(".")
            model = path_list[1]
            if len(path_list) == 3:
                product_name = path_list[2]
            else:
                product_name = None
        model_url = json.loads(RHIniParser(ini_path).get_ini_info("MODEL_URL", "MODEL_URL_DATA"))[model]
        ini_contant = get_ini_default_contant(ini_path, api, product_name)

        # 若为移动端接口，则一般为默认443或则80端口，需要把端口号去掉    --如有需要处理的，自行添加。
        if "newWechat" in model or "bplan" in model:
            main_url = main_url.replace(version_port, "")

        if ".db" not in api and ".dmldb" not in api:
            # 读取对应api接口的默认值，请求方式，出入参设置，正则表达式，特定返回值
            default_contant = ini_contant[0]
            request_method = ini_contant[1]
            in_para_dic = ini_contant[2]
            out_para_dic = ini_contant[2]
            default_re_set = ini_contant[3]

            # 原始数据转成dict
            default_contant = transfor_to_dict(default_contant)

            if "||" in data_source[i * 2 + 1 - j]:  # 对rf的表格的取值，替换列的，注意替换项必须和url里面的一致
                urlparam = data_source[i * 2 + 1 - j].split("||")[1]
            # 替换urlinput设置的变量--url
            interface_name = change_in_html_urldic(in_para_dic, dic_args, interface_name, urlparam)

            #szx特殊处理
            if interface_name == 'savePolicyInfo.do' and product_name[-2:]=='01':
                wtr_num=0
                scanmock_result = query_scanmock_result(str(default_contant["applyBarCode"])[:-2])
                while (not scanmock_result.flag) and wtr_num <= 5:
                    scanmock_result=query_scanmock_result(str(default_contant["applyBarCode"])[:-2])
                    # print 'waiting %s' % Settings.EXTREME_TIMEOUT
                    sleep(Settings.EXTREME_TIMEOUT)
                    wtr_num +=1
            if api == 'addApplyInfo/passSaveApplyInfo.do':
                sleep(20)

            # 替换设置的参数值
            change_para_html(default_contant, data_source[i * 2 + 1 - j].split("||")[0])  # data_source[1]    data_source[3]...
            #szx特殊处理
            if interface_name == 'savePolicyInfo.do' and product_name[-2:] == '02':
                dic_args = uw_query_ins_or_prem(str(default_contant["applyBarCode"]), dic_args)
            # 替换in out设置的变量--data
            change_in_html_dic(in_para_dic, dic_args, default_contant)

            # 更新token， 放入请求hearder中
            authorization = change_in_token_dic(in_para_dic, dic_args, authorization)
            # ============请求hearder组装 如有需要，自行处理====================
            # 微信快易投需要用token验证
            if "newWechat" in model:
                headers = dict(headers_wechat, **{"authorization": "Bearer " + authorization})

            '''上传照片接口单独处理获取照片'''
            if api.__contains__("imageUploding"):
                local_files = json.loads(RHIniParser(ini_path).get_ini_info("UPLOAD", "UPLOAD_DEFAULT_FILES"))[api]
                upload_files = upload_files_format(local_files, path)
            print "请求接口:  " + main_url + model_url + interface_name
            # print default_contant

            # 发送请求
            response_html = html_request(main_url+model_url+interface_name, default_contant, cookies, upload_files, request_method, headers)
            data = Core.rh_replace_data(data_source[i * 2 + 2-j])
            for i in data:
                res = rh_html_check_result(i, response_html)
                if "[success]" not in res:
                    logger.error("%s failed:\n***********post data:\n%s\n***********response data:%s" % (api,default_contant,response_html))
                Verify.should_contain(res, "[success]")
            # 获取正则表达式列表
            default_re = default_re_set.split(";")
            # 存储特定返回值
            out = get_out_html_dic(out_para_dic, response_html, default_re)
            dic_args = get_new_dic(dic_args, out)
            print "%s:%s" %(api,dic_args)
        # ===================================================================================
        # ============若无DB检查点，可以暂时忽略该部分代码，若需要添加，自行修改====================
        elif ".db" in api:
            j += 2
            # 对于DB校验sql取数，产品取db前一个接口对应的产品。
            # 获取检验的sql
            sql_list = ini_contant
            # 避免程序入库事务还未完成就执行DB校验，故等待1秒
            sleep(1)
            # 注意 此处传过去的sql为list（多条）  格式：saveApproval.slis.db
            if 'msp' in api_name:
                result = check_db(sql_list, version, api.split('.')[1], dic_args["applyBarCode"].split())
            else:
                result = check_db(sql_list, version, api.split('.')[1])
            if not result.flag:
                logger.info(result.msg, "%s failed" % api)
                print result.msg, "%s failed" % api
            Verify.should_be_true(result.flag)
            print "%s success" % api
            logger.info("%s success" % api)
        # ==========若有需要，执行回滚脚本======================================#
        else:
            j += 2
            # 对于DB回滚sql取数，产品取db前一个接口对应的产品。
            # 获取需要回滚的sql
            rollback_sqllist = ini_contant

            # 避免程序入库事务还未完成就执行DB校验，故等待1秒
            sleep(1)
            # 执行回滚操作
            try:
                dml_db(rollback_sqllist, version, api.split('.')[1])
                print "%s success" % api
                logger.info("%s success" % api)
            except Exception, e:
                raise Exception("error occur in sql rollback, %s", str(e))

#szx特殊处理
def query_scanmock_result(barcode):
    u'''
    功能描述: MOCK结果查询
    '''
    result = Result()
    try:
        sqltest = RHOracle(usr=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_dbcheck_usr"],
                           pwd=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_pwd"],
                           ip=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_host"],
                           port=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_port"],
                           db=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_name"])
        sql=EnvSetting.SQL_DIC["UW_SCANMOCK_RESULT"]%barcode+"%'"
        result.flag =sqltest.check_query_count(sql)
        # logger.info("SQL scanmock query success,result: " + str(result.flag))
    except Exception, e:
        print e
    finally:
        return result

#szx特殊处理
def uw_query_ins_or_prem(apply_bar_code,dic_args):
    u'''
    功能描述: 查询保费保额
    '''
    try:
        sqltest = RHOracle(usr=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_dbcheck_usr"],
                           pwd=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_pwd"],
                           ip=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_host"],
                           port=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_port"],
                           db=EnvSetting.WEB_DEFAULT_DIC["uw"]["db_name"])
        sql_applyno=EnvSetting.SQL_DIC["UW_QUERY_APPLY_NO"]%(apply_bar_code)
        apply_no=sqltest.fetchone_query(sql_applyno)[0]
        product_num=len(sqltest.fetchall_query(EnvSetting.SQL_DIC["UW_QUERY_INS_AND_PREM"]%('sum_insured',apply_no)))
        dic_args["sumInsured"] = unicode(sqltest.fetchone_query(EnvSetting.SQL_DIC["UW_QUERY_INS_AND_PREM"] % ('sum_insured', apply_no))[0])
        dic_args["mainAnnStandardPrem"] = unicode(sqltest.fetchone_query(EnvSetting.SQL_DIC["UW_QUERY_INS_AND_PREM"] % ('ann_standard_prem', apply_no))[0])
        dic_args["fillInPrem"] = dic_args["mainAnnStandardPrem"]
        k=2
        while k < product_num+1:
            dic_args["addSumInsured%s"%(k-2)] = unicode(sqltest.fetchone_query(EnvSetting.SQL_DIC["UW_QUERY_INS_AND_PREM"] % ('sum_insured', apply_no)+ " and prod_seq='%s'"%k)[0])
            dic_args["addAnnStandardPrem%s"%(k-2)] = unicode(sqltest.fetchone_query(EnvSetting.SQL_DIC["UW_QUERY_INS_AND_PREM"] % ('ann_standard_prem', apply_no) + " and prod_seq='%s'"%k)[0])
            dic_args["fillInPrem"]=unicode(float(dic_args["fillInPrem"])+float(dic_args["addAnnStandardPrem%s"%(k-2)]))
            k=k+1
    except Exception, e:
        print e
    finally:
        return dic_args


def check_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    result = sqlobj.execute_query_many(sql_list, param)
    return result


def dml_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    sqlobj.execute_rollback_sql(sql_list, param)


def check_db(sql_list, version, sid='slis', param=[]):
    result = check_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"], EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                       EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)
    return result


def dml_db(sql_list, version, sid='slis', param=[]):
    dml_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"], EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                 EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)


def html_replace_data(data):
    data = str(data).strip().replace("\n","").replace("”","\"").replace("‘","\'").replace("’","\'").replace("；",";").decode("utf-8")
    if data.endswith(";"):
        data = data[:-1]
    return data.split(";")


# 替换html内容
def change_para_html(html_cont, data):
    if data == "":
        return html_cont

    replace_data = html_replace_data(data)
    for data in replace_data:
        if "=" not in data:
            raise Exception("error format,not found =")
        try:
            if ":=" not in data:
                raise Exception("error format")
            sval = get_var(data.split(":=")[1])
            name = data.split(":=")[0]
            # 对参数做num，str区分 数字：222222， str：'222222'
            if sval != "":
                if is_numeric(sval):
                    sval = int(sval)
                elif "\'" in sval:
                    sval = sval.replace("\'", "")
                elif sval.startswith("[") or sval.startswith("{"):
                    sval = eval_str(sval)
            # 对入参类型为bool, null的处理
            if sval == 'false':
                sval = False
            elif sval == 'true':
                sval = True
            elif sval == 'null' or sval == "":
                sval = None
            scmd = '''html_cont[%s]="%s" ''' % (name, sval)
            html_cont[name] = sval
        except Exception, e:
            raise Exception("error after %s, %s" % (scmd, str(e)))
    return html_cont


# html默认form表单请求
def html_request(url, html, cookies={}, files={}, method="post", headers={}):
    if method == "get":
        response = session.get(url, params=html, headers=headers, cookies=cookies, verify=False)
    elif method == "uploadfiles":
        # headers = {'Content-Type': 'multipart/form-data'}
        headers = {}
        response = session.post(url, files=files, data=html, headers=headers, cookies=cookies, verify=False)
    else:
        response = session.post(url, data=html, headers=headers, cookies=cookies, verify=False)
    # print response.text
    return response.text


# 结果校验
# 非json格式返回模板为:ResultInfoDesc:=自动核保通过(包含的message);
# json返回模板为：error:=交易成功   其中实际值为："error":"交易成功"
# 返回为list，模板为：1.aaa:=bbbb   或者 1:=bbbb
def rh_html_check_result(input, response_json):
    data = str(input).strip().replace("\n", "").replace("”", "\"").replace("‘", "\'").replace("’", "\'").replace(
        "；", ";")
    if data is None:
        raise Exception("error format,prepareResult is none.")

    flag = False
    # eval()对特殊值处理
    # null = ""
    # true = True
    # false = False
    # 返回结果为list[]或者 json格式 比较
    if response_json.startswith("[") or response_json.startswith("{"):
        response_json = eval_str(response_json)         # str转成list
        cmp_result = Core.rh_check_result(input, response_json)
        if "[success]"in cmp_result:
            flag = True
        else:
            return "[fail]:response data do not contains %s." % data
    # 返回结果为text
    else:
        except_message = data.split(":=")[1]
        if response_json.__contains__(except_message):
            flag = True
        else:
            return "[fail]:response data do not contains %s." % data
    if flag:
        return "[success]:response data contains %s." % data


# 替换登录请求参数--MSP登录修改参数中端口号特殊处理
def change_login_dic(api_name, login_data, port="12021"):
    new_dict = {}
    for key in login_data:
        new_dict[key] = EnvSetting.ENV_DEF_DIC.get(api_name).get(key, "")
        try:
            if "toURL" in key:
                new_dict[key] = change_url_port(new_dict[key], port)
                # 替换对应登录参数
                login_data[key] = new_dict[key]
        except Exception, e:
            raise Exception("error change, %s, %s" % (key, str(e)))
    return login_data


# 替换html 设置的变量
def change_in_html_dic(sdic, new_dic, html_cont):
    if new_dic != {}:
        if sdic.get("input", "") != "":
            for (sname, sval) in sdic.get("input", "").items():
                try:
                    name = sname
                    vaule = new_dic[sval]
                    html_cont[name] = vaule
                except Exception, e:
                    raise Exception("error after change, %s, %s" % (name, str(e)))


# 获取接口返回的json内容，取对应字段存到sdic
def get_out_html_dic(sdic, response_json, pattern):
    out = {}
    if sdic.get("output", "") != "":
        if '<' not in response_json and '{' in response_json and '}' in response_json:
            response_json = response_json[response_json.find('{'):response_json.rfind('}')+1]
        i = -1
        if response_json.startswith("{") or response_json.startswith("["):
            if response_json.startswith("{"):
                # 返回若为response.text 则需要转成json，若为response.json()，则不用
                response_json = json.loads(response_json)
            for (sname, sval) in sdic.get("output", "").items():
                i += 1
                try:
                    out[sname] = get_nestdict_value(sname, response_json)
                except Exception, e:
                    logger.info("out arg %s not find" % sname)
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


def get_new_dic(new_out_dic, out):
    for (k, v) in out.items():
        new_out_dic[k] = v
    return new_out_dic


# a=111&b=222 原生form表单格式转成dict
def transfor_to_dict(data):
    if isinstance(data, dict):
        properties=data
    else:
        listdata = data.split("&")
        # print listdata
        properties = {}
        # a = 0
        for line in listdata:
            # a += 1
            if line.find("=") > 0:
                strs = line.replace("\n", "").replace("\t|\n", "").split("=")
                properties[strs[0]] = strs[1]
    return properties


# JSESSIONID=0a51;_rf_profile=pppp; 等格式转成dict       处理cookies
def str_to_dict(data, pattern01, pattern02):
    listdata = data.replace(" ", "").split(pattern01)
    dictdata = {}
    for i in listdata:
        nv = i.split(pattern02)
        dictdata[nv[0]] = nv[1]
    return dictdata


# 上传照片处理
def upload_files_format(filedata, path):
    upload_files = {}
    for key in filedata.keys():
        filedata[key] = path + filedata[key]
    for (k, v) in filedata.items():
        vfile = open(v, 'rb')
        upload_files[k] = vfile
    return upload_files


# 替换不同版本url, port方法
def change_url_port(url, change_port, change_url=""):
    if "443" is not change_port:
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


# 截取-获取登录地址 域名+端口
def get_login_url(url):
    if "RH_" in url:
        k = [m.start() for m in re.finditer("/", url)][2]
        url = url[0:k]
    return url


# 替换url in out设置的变量
def change_in_html_urldic(sdic, new_dic, url, data=""):
    # 替换url中设置替换的变量
    if data != "":
        replace_data = html_replace_data(data)
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
def change_in_token_dic(sdic, new_dic, token):
    if new_dic != {}:
        if sdic.get("headinput", "") != "":
            for (sname, sval) in sdic.get("headinput", "").items():
                try:
                    name = sname
                    token = new_dic[sval]
                except Exception, e:
                    raise Exception("error after change, %s" % name)
    return token


# json合并    嵌套的json取内值合并成一个
# Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]} 输出： Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
def get_format_dict(dictdata):
    for (k, v) in dictdata.items():
        if isinstance(v, dict):
            new_dict = v.copy()
            dictdata.pop(k)
            dictdata = dict(dictdata.items() + new_dict.items())
            if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                return dictdata
            else:
                return get_format_dict(dictdata)
    return dictdata


# 获取字典中的objkey对应的值，适用于字典嵌套
# dict:字典
# objkey:目标key
# default:找不到时返回的默认值
# PS:若嵌套的json或者list中有key名称相同，则只能获取到第一个key的值，故只能取第一个key做对比
def dict_get(dict, objkey, default=None):
    tmp = dict
    for k, v in tmp.items():
        if k == objkey:
            return v
        else:
            if type(v) is types.DictType:
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
            elif type(v) is types.ListType:
                for val in v:
                    ret = dict_get(val, objkey, default)
                    if ret is not default:
                        return ret
    return default


# 获取复杂嵌套list，json对应的下标（key）值
# 格式：keytag： "2.a"      dict_data：[{"a": "111", "b": 222}, "bbbb", {"a": "555", "b": 222}]
def get_nestdict_value(keytag, dict_data):
    sname = keytag.strip()
    obj = scmd = realval = ""
    for i in sname.split("."):
        if is_numeric(i):
            obj = "%s[%s]" % (obj, i)
        else:
            obj = "%s['%s']" % (obj, i)
    scmd = "%s%s" % ("dict_data", obj)
    try:
        realval = eval(scmd)
    except:
        return "[Failed]:cmd change error,eval(%s)" % scmd
    return realval


# 判断s是否为数字
def is_numeric(s):
    return all(c in "0123456789" for c in s)


# eval()方法二次封装
def eval_str(str_data):
    # eval()对特殊值处理
    null = ""
    true = True
    false = False
    return eval(str_data)


# 封装取ini默认数据方法
def get_ini_default_contant(ini_path, api=None, product_name=None):
    if api is None and product_name is None:
        default_contant = json.loads(RHIniParser(ini_path).get_ini_info("DATA", "ENV_DEFAULT_DATA"))
        request_method = json.loads(RHIniParser(ini_path).get_ini_info("METHED", "REQUEST_METHOD"))
        in_out_para_dic = json.loads(RHIniParser(ini_path).get_ini_info("PARA", "DICT_IN_OUT"))
        default_re_set = json.loads(RHIniParser(ini_path).get_ini_info("RE", "RE_SET"))
        sql_list = json.loads(RHIniParser(ini_path).get_ini_info("SQL", "SQL_DIC"))
        rollback_sqllist = json.loads(RHIniParser(ini_path).get_ini_info("DML_SQL", "DMLSQL_DIC"))
        return default_contant, request_method, in_out_para_dic, default_re_set, sql_list, rollback_sqllist
    elif product_name is None:
        if ".db" in api:
            sql_list = json.loads(RHIniParser(ini_path).get_ini_info("SQL", "SQL_DIC")).get(api, [])
            return sql_list
        elif ".dmldb" in api:
            rollback_sqllist = json.loads(RHIniParser(ini_path).get_ini_info("DML_SQL", "DMLSQL_DIC")).get(api, [])
            return rollback_sqllist
        else:
            default_contant = json.loads(RHIniParser(ini_path).get_ini_info("DATA", "ENV_DEFAULT_DATA")).get(api)
            request_method = json.loads(RHIniParser(ini_path).get_ini_info("METHED", "REQUEST_METHOD")).get(api, "")
            in_out_para_dic = json.loads(RHIniParser(ini_path).get_ini_info("PARA", "DICT_IN_OUT")).get(api, {})
            default_re_set = json.loads(RHIniParser(ini_path).get_ini_info("RE", "RE_SET")).get(api, "")
            return default_contant, request_method, in_out_para_dic, default_re_set
    else:
        if ".db" in api:
            sql_list = json.loads(RHIniParser(ini_path).get_ini_info("SQL", "SQL_DIC")).get(api, {}).get(product_name, [])
            return sql_list
        elif ".dmldb" in api:
            rollback_sqllist = json.loads(RHIniParser(ini_path).get_ini_info("DML_SQL", "DMLSQL_DIC")).get(api, {}).get(product_name, [])
            return rollback_sqllist
        else:
            default_contant = json.loads(RHIniParser(ini_path).get_ini_info("DATA", "ENV_DEFAULT_DATA")).get(api).get(product_name)
            request_method = json.loads(RHIniParser(ini_path).get_ini_info("METHED", "REQUEST_METHOD")).get(api, {}).get(product_name, "")
            in_out_para_dic = json.loads(RHIniParser(ini_path).get_ini_info("PARA", "DICT_IN_OUT")).get(api, {}).get(product_name, {})
            default_re_set = json.loads(RHIniParser(ini_path).get_ini_info("RE", "RE_SET")).get(api, {}).get(product_name, "")
            return default_contant, request_method, in_out_para_dic, default_re_set


if __name__ == '__main__':
    # data_source = ["msp.branchAttendance:getBranchAttendanceList",
    #                "branchCode:='86480000';queryDate:=2018-02",
    #                u"flag:=Y"
    #                # "mspNo:=A000000000056258",
    #                # u"countryList.0.countryName:=申根协议国"
    #                ]

    data_source = ["msp.apply.1;msp.apply.1;msp.apply;msp.apply;msp.apply;msp.apply;msp.apply;msp.apply:saveClient.do;saveHealthInform.do;imageUploding.do;ownCheck.do;getPhonePayPwd;pay.do;issueByBarCode.do;issueByBarCode.slis.db",
                   "mspApplyInfo.mspNo:=$g_no$;mspNo:=$g_no$;insureds.clientInfo.clientName:=$g_name$;insureds.clientInfo.idno:=$g_idcard$(19900101,2,01);insureds.clientInfo.sexCode:='2';insuredsBirthDay:=1990-01-01;insureds.clientEmail.emailAddress:=$g_email$ ;insureds.mobilePhone.phoneNo:=$g_mobile$;insureds.homeAddress.detailAddress:=$g_addrs$;applicant.contactAddress.detailAddress:=$g_addrs$",
                   u"ResultInfoDesc:=健康告知",
                   "mspApplyInfo.mspNo:=$g_no$;mspNo:=$g_no$",
                   u"mResultInfoDesc:=投保规则检查通过",
                   "mspNo:=$g_no$",
                   u"ResultInfoDesc:=成功",
                   "mspNo:=$g_no$",
                   u"ResultInfoDesc:=自动核保通过",
                   "mspNo:=$g_no$",
                   u"ResultInfoDesc:=",
                   "mspNo:=$g_no$",
                   u"0.error:=交易成功",
                   "mspNo:=$g_no$",
                   u"ResultInfoDesc:=投保成功"
                   ]
    html_model_pub(data_source, "0118", "python")

    # data_source=[
    #
    # ]
    # html_model_pub(data_source, "0118", "python")
