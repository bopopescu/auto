# encoding=UTF-8
import os
import re

import requests
import ssl
from bs4 import BeautifulSoup
from robot.api import logger
from robot.libraries.BuiltIn import _Verify

from business.conf import EnvSetting
from titanrun.common import Core
from titanrun.common.Core import get_var
from titanrun.common.DbOperate import RHOracle
from Result import Result
import titanrun.config.Settings as Settings

def xml_model_pub(data_source,model="ride"):
    dic_args = {}
    result = Result()
    Verify = _Verify()
    j = 0
    if model == "ride":
        path = os.path.abspath('.')
    else:
        path = os.path.abspath('../..')
    data_source_apis = data_source[0].split(":")
    apis = xml_replace_data(data_source_apis[1])
    product_path = xml_replace_data(data_source_apis[0])



    project_name = product_path[0].split(".")[0]
    api_len = len(apis)

    ini_path = "%s/config/api/bank/%s/para_configuration.ini" % (path, project_name)

    ybt_def_dic =EnvSetting.ENV_DEF_DIC
    ybt_pro_dic = ybt_def_dic.get(project_name)
    Settings.CASE_GEN_DIC = {}
    for i in xrange(api_len):
        api = Core.rh_get_api_name(apis[i])
        if ".xml" in api:
            if len(product_path) == 1:
                project_all_path = "/".join(product_path[0].split("."))
                model_path = '%s/config/api/bank/%s/' % (path, project_all_path)
            else:
                project_all_path = "/".join(product_path[i-j/2].split("."))
                model_path = '%s/config/api/bank/%s/' % (path, project_all_path)
            xml = model_path+api
            in_para_dic = Core.rh_load_default_api_dic(api, ini_path, "PARA", "DICT_IN_OUT")
            soup = get_soup(xml)
            change_in_soup_dic(in_para_dic, dic_args, soup)
            change_para_soup(soup, data_source[i * 2 + 1-j])
            response_soup = soup_post(ybt_pro_dic["url"], soup)
            data = Core.rh_replace_data(data_source[i * 2 + 2-j])
            for i in data:
                res = rh_soup_check_result(i, response_soup)
                if "[success]" not in res:
                    logger.error("%s failed:\n***********post data:\n%s\n***********response data:%s" % (api,soup,response_soup))
                Verify.should_contain(res, "[success]")
            out_para_dic = Core.rh_load_default_api_dic(api, ini_path, "PARA", "DICT_IN_OUT")
            out = get_out_soup_dic(out_para_dic, response_soup)
            dic_args = get_new_dic(dic_args, out)
            print "%s:%s" %(api,dic_args)
        else:
            j+=2
            # if project_name=="ccb":
            #     p_num = dic_args["InsPolcy_No"]
            # else:
            p_num = dic_args["PolNumber"]
            if api =="bia_to_core.db":
                result = bia_to_core(p_num, ybt_pro_dic["db_bia_usr"], ybt_pro_dic["db_bia_pwd"],
                                         ybt_pro_dic["db_ip"], ybt_pro_dic["db_name"])
            elif api =="fin_check.db":
                result = fin_check(p_num,ybt_pro_dic["db_fin_usr"],ybt_pro_dic["db_fin_pwd"],ybt_pro_dic["db_ip"],ybt_pro_dic["db_name"])
            elif api =="biab_to_core.db":
                result = biab_to_core(p_num, ybt_pro_dic["db_bia_usr"], ybt_pro_dic["db_bia_pwd"],ybt_pro_dic["db_ip"], ybt_pro_dic["db_name"])
            elif api == "upload_file":
                result = upload_file(ybt_pro_dic, dic_args, path, name="pub.jpg")
            if not result.flag:
                print result.msg
                "%s failed" %api
            Verify.should_be_true(result.flag)
        logger.info("%s success" %api)
        print "%s success" % api

def bia_to_core(pono,db_usr,db_pwd,db_ip,db_name):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd,ip=db_ip,db=db_name)
    result = sqlobj.bia_to_core_batch(pono)
    return result

def biab_to_core(pono,db_usr,db_pwd,db_ip,db_name):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd,ip=db_ip,db=db_name)
    result = sqlobj.biab_to_core_batch(pono)
    return result

def fin_check(pono,db_usr,db_pwd,db_ip,db_name):
    sqlobj = RHOracle(usr=db_usr, pwd=db_pwd,ip=db_ip,db=db_name)
    result = sqlobj.fin_check(pono)
    return result

def upload_file(ybt_pro_dic,dic_args,path,name="pub.jpg"):
    result = Result()
    url = ybt_pro_dic["upload_url"]
    file_path="%s/config/file/%s" %(path,name)
    img_name = "20171027_%s_P01_110102199202022211_01.jpg" % dic_args["PolNumber"]
    img = {'img': (img_name,open(file_path, 'rb'), 'image/jpg')}
    response = requests.post(url, files=img,verify=False)
    if "999999" in response.content:
        result.flag = True
    else:
        result.msg = response.content.decode("gbk")
        print result.msg
    return result


def get_xml_name(path,name):
    return path+name

def xml_replace_data(data):
    data = str(data).strip().replace("\n","").replace("”","\"").replace("‘","\'").replace("’","\'").replace("；",";").decode("utf-8")
    if data.endswith(";"):
        data = data[:-1]
    return data.split(";")

def change_para_soup(soup,data):
    if data == "":
        return soup

    replace_data = xml_replace_data(data)
    for data in replace_data:
        if "=" not in data:
            raise Exception("error format,not found =")
        try:
            if ":=" not in data:
                raise Exception("error format")
            # sval = data.split(":=")[1]
            sval = get_var(data.split(":=")[1])
            name =sname = data.split(":=")[0]
            sflag = 0
            if "." in sname:
                name = sname.split(".")[0]
                sflag = sname.split(".")[1]
            scmd = '''soup.find_all("%s")[%s].string="%s" ''' % (name, sflag,sval)
            exec scmd
        except Exception, e:
            raise Exception("error cmd,%s" % scmd)
    return soup

def get_soup(xml_path):
    data=open(xml_path).read()
    soup = BeautifulSoup(data, "xml")
    return soup

def soup_post(url,soup):
    headers = {'Content-Type': 'application/xml', 'charset': 'GBK'}
    soup_data = soup.prettify().encode("GBK").replace("\n", "")
    #农行报文头进行过加密处理
    if "abcii" in url:
        soup_data = soup_data.replace('<?xml version="1.0" encoding="utf-8"?>', 'X1.0000000001111111100000                                        00000000')
    #第三方支付走的是内部接口，要求报文头中一定是GBK
    if "web_allinpay" or "yqzl_gnete" or "msp_gnete_pay" in url:
        soup_data = soup_data.replace('<?xml version="1.0" encoding="utf-8"?>','<?xml version="1.0" encoding="GBK"?>')
    soup_data = replace_xml_space(soup_data)
    #广银联和微投保要输入带空格的时间格式字段，报文中用*代替，此处再处理成原有格式
    if "yqzl_gnete" or "msp_gnete_pay"  or  "web_wtb" in url:
        soup_data = soup_data.replace("*"," ")
    #response = requests.post(url, soup_data,headers=headers)
    #关闭ssl证书验证
    requests.packages.urllib3.disable_warnings()
    response = requests.post(url, soup_data, headers=headers,verify=False)
    text=response.text
    if response.status_code!=200:
        raise Exception(text)
    #建行与交行返回响应格式处理
    #农行返回响应无标准xml报文头
    if "ccbii" in url:
        response_data = text[text.find("<?xml"):]
    elif "bocii" in url:
        response_data = text[text.find("<?xml"):]
    elif "abcii" in url:
        response_data = text[text.find("<ABCB2I>"):].encode("GBK")
    else:
        response_data = text[text.find("<?xml"):].encode("GBK")
    response_soup = BeautifulSoup(response_data, "xml")
    return response_soup

def rh_soup_check_result(input, soup):
    data = str(input).strip().replace("\n", "").replace("”", "\"").replace("‘", "\'").replace("’", "\'").replace(
        "；", ";")
    if data=="":
        return "[success]"
    if ":=" not in data:
        raise Exception("error format,not found :=")

    svalue = get_var(data.split(":=")[1])
    name = sname = data.split(":=")[0]
    sflag = 0
    realval = ""
    if "." in sname:
        name = sname.split(".")[0]
        sflag = sname.split(".")[1]
    scmd = '''realval = soup.find_all("%s")[%s].string ''' % (name, sflag)
    try:
        exec(scmd)
    except:
        return "[Failed]:cmd change error,%s" % scmd
    svalue = str(svalue).decode("utf-8")
    realval = str(realval).decode("utf-8")
    if str(svalue).strip() == str(realval).strip():
        pass
    elif svalue == "不为空":
        if realval == "{}" or realval == "[]":
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif svalue == "不为0":
        if realval == "0":
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif svalue == "为空":
        if realval == "{}" or realval == "[]" or realval == '':
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif svalue == "为0":
        if realval == "0":
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif "<INCLUDE>" in svalue:
        svalue = svalue.split("<")[0]
        if str(svalue) in realval:
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif "<EXCEPT>" in svalue:
        svalue = svalue.split("<")[0]
        if str(svalue) in realval:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
        else:
            return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)

    elif ".00" in str(realval):
        if str(svalue) == str(realval[:-3]):
            pass
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif str(realval) == '0.0':
        if str(svalue) in ["0.0", "0.00"]:
            pass
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    elif str(svalue) == "null":
        if realval == None:
            pass
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    else:
        if str(svalue) == "" and (realval == "[]" or realval == "{}"):
            pass
        else:
            return "[Failed]:%s expect is %s,real is %s." % (sname, svalue, realval)
    return "[success]:%s expect is %s,real is %s." % (sname, svalue, realval)

def change_in_soup_dic(sdic,new_dic,soup):
    if new_dic!={}:
        if sdic.get("input", "") != "":
            for (sname, sval) in sdic.get("input", "").items():
                sflag = 0
                if "." in sname:
                    name = sname.split(".")[0]
                    sflag = sname.split(".")[1]
                else:
                    name = sname
                scmd = '''soup.find_all("%s")[%s].string=new_dic["%s"]''' % (name, sflag, sval)
                exec scmd

def get_out_soup_dic(sdic,soup):
    out = {}
    if sdic.get("output","")!="":
        for (sname,sval) in sdic.get("output","").items():
            sflag = 0
            if "." in sval:
                name = sval.split(".")[0]
                sflag = sval.split(".")[1]
            else:
                name =sval
            scmd = '''out["%s"]=soup.find_all("%s")[%s].string''' % (sname,name, sflag)
            try:
                exec scmd
            except Exception,e:
                logger.info("out arg %s not find" %sname)
    return out

def get_new_dic(new_out_dic,out):
    for (k,v) in out.items():
        new_out_dic[k] = v
    return new_out_dic

def replace_xml_space(data):
    pattern = re.compile(r'>.*?<')
    match = pattern.findall(data)
    for item in match:
        data = data.replace(item, item.replace(" ", ""))
    return data

def change_str_arg(data,*args):
    for i in args:
        data = data.replace("%s",str(i),1)
    return data


if __name__=="__main__":
    # data_source = ["cmb.2002:cmb_under_write.xml;cmb_issue.xml;bia_to_core.db","GovtID.0:=$g_idcard$;GovtID.1:=$g_idcard$;DialNumber.2:=$g_mobile$;DialNumber.5:=$g_mobile$;AddrLine.0:=$g_mail$;AddrLine.1:=$g_mail$","ResultInfoDesc:=交易成功","GovtID.0:=$g_idcard$;GovtID.1:=$g_idcard$;DialNumber.2:=$g_mobile$;DialNumber.5:=$g_mobile$;AddrLine.0:=$g_mail$;AddrLine.1:=$g_mail$","ResultInfoDesc:=交易成功"]
    # data_source = [
    #     "ccb.2003:ccb_pre_issue.xml;ccb_confirm_issue.xml;bia_to_core.db","Rcgn_Nm:=$g_name$;Plchd_Nm:=$g_name$;Plchd_Brth_Dt.0:=19710904;Rcgn_Brth_Dt.0:=19710904;Plchd_Crdt_No.0:=$g_idcard$(19710904,2,01);RspbPsn_Nm:=$g_idcard$(19710904,2,01);Plchd_Move_TelNo.0:=$g_mobile$;Plchd_Email_Adr.0:=$g_mail$;Rcgn_Crdt_No.0:=$g_idcard$(19710904,2,01);Rcgn_Move_TelNo.0:=$g_mobile$;Rcgn_Email_Adr.0:=$g_mail$","SYS_RESP_DESC:=交易成功","","SYS_RESP_DESC:=成功"]
    data_source = ["cmb.2002:cmb_under_write.xml;cmb_issue.xml","FullName.0:=$g_name$;FullName.1:=$g_name$;GovtID.0:=$g_idcard$;GovtID.1:=$g_idcard$;DialNumber.2:=$g_mobile$;DialNumber.5:=$g_mobile$;AddrLine.0:=$g_mail$;AddrLine.1:=$g_mail$","ResultInfoDesc:=交易成功","FullName.0:=$g_name$;FullName.1:=$g_name$;GovtID.0:=$g_idcard$;GovtID.1:=$g_idcard$;DialNumber.2:=$g_mobile$;DialNumber.5:=$g_mobile$;AddrLine.0:=$g_mail$;AddrLine.1:=$g_mail$","ResultInfoDesc:=交易成功"]
    xml_model_pub(data_source, "python")

