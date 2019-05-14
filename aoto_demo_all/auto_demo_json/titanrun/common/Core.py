# coding=utf-8
import ConfigParser
import json
import os
import random
import string
import time
import requests
import sys
from datetime import date,datetime,timedelta
import codecs
import csv
from bs4 import BeautifulSoup

from business.conf import EnvSetting
from titanrun.common.DbOperate import RHOracle
from titanrun.common.Identity import generate_id, generate_phone, generate_name, get_no, get_gendercode_by_id, \
    get_bar_code, generate_mail,md5_format, get_timestamp,get_image_base64encode, g_random
from titanrun.config.DistrictsAll import Districts
from selenium import webdriver

# from titanrun.config.Settings import Settings.CASE_GEN_DIC
import  titanrun.config.Settings as Settings

reload(sys)
sys.setdefaultencoding('utf-8')

def genneratorId():
    id = Districts.keys()[random.randint(0, len(Districts.keys()))] #地区项
    id = id + str(random.randint(1930,2013)) #年份项
    da  = date.today()+timedelta(days=random.randint(1,366)) #月份和日期项
    id = id + da.strftime('%m%d')
    id = id+ str(random.randint(100,300))#，顺序号简单处理

    i = 0
    count = 0
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] #权重项
    checkcode ={'0':'1','1':'0','2':'X','3':'9','4':'8','5':'7','6':'6','7':'5','8':'5','9':'3','10':'2'} #校验码映射
    for i in range(0,len(id)):
       count = count +int(id[i])*weight[i]
    id = id + checkcode[str(count%11)] #算出校验码
    return str(id)

def get_session():
    return requests.Session()

def rh_post_session(url,api,data,session):
    all_url = "%s%s" %(url,api)
    response = session.post(all_url, data)
    res=json.loads(str(response.text.encode("utf-8")))
    return res

def rh_post_json(url,data,session=""):
    if session == "":
        response = requests.post(url, json=data)
    else:
        response = session.post(url, json=data)
    print response,response.text
    if response.status_code!=200:
        raise Exception(response.text)
    res = json.loads(str(response.text.encode("utf-8")))
    return res

def rh_post(url,data,session=""):
    # headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept-Language': 'zh-CN,zh;q=0.9','Accept-Encoding': 'gzip, deflate, br'}
    if session == "":
        response = requests.post(url, data,verify=False)
    else:
        # response = session.post(url, data,headers=headers,verify=False)
        response = session.post(url, data, verify=False)
    if response.status_code!=200:
        raise Exception(response.text)
    print response,response.text
    # res = json.loads(str(response.text.encode("utf-8")))
    res=response.text
    if 'html' in res:
        res_xml = BeautifulSoup(str(response.text.encode("utf-8")), features='xml')
        res = dict([(item.name, item.text) for item in res_xml.find_all()])
    elif 'jsonp' in res:
        res=res[res.find('{'):res.find(')')]
        res=json.loads(str(res.encode("utf-8")))
    elif res!='':
        res = json.loads(str(res.encode("utf-8")))
    return res

def rh_get(url,data=None,session=""):
    if session == "" :
        response = requests.get(url,data,verify=False)
    else:
        response = session.get(url,verify=False)
    print response,response.text
    res=response.text
    if response.status_code!=200:
        raise Exception(response.text)
    if 'html' in res:
        res_xml = BeautifulSoup(str(response.text.encode("utf-8")), features='xml')
        res = dict([(item.name, item.text) for item in res_xml.find_all()])
    elif 'jsonp' in res:
        res=res[res.find('{'):res.find(')')]
        res=json.loads(str(res.encode("utf-8")))
    elif res!='':
        res = json.loads(str(res.encode("utf-8")))
    return res

def is_numeric(s):
    if s.startswith("-") or s.startswith("+") or "." in s:
        return all(c in "0123456789.+-" for c in s)
    else:
        return all(c in "0123456789" for c in s)

def biam_random_change(name,data):
    if name=="cmrh.policy.product.GBatchIssue":
        id = genneratorId()
        datestr = (date.today() + timedelta(days=1)).strftime("%Y%m%d")
        idstr = '0.applicantID:="%s";0.insuredID:="%s";0.passengerID:="%s";0.policyFlights.0.flightDate:="%s" ' %(id,id,id,datestr)
        rh_change_dic(data,idstr)

def rh_change_dic(sdic,data):
    if data == "":
        return sdic
    data = rh_replace_data(data)
    for i in data:
        if "=" not in i:
            raise Exception("error format,not found =")
        try:
            sname = str(i).split(":=")[0].strip()
            svalue = get_var(str(i).split(":=")[1].strip())
            obj = ""
            if svalue.startswith("["):
                try:
                    svalue = eval(svalue)
                except Exception,e:
                    raise Exception("error format")
            for i in sname.split("."):
                if is_numeric(i):
                    obj = "%s[%s]" %(obj,i)
                else:
                    obj = "%s['%s']" %(obj,i)
            scmd ='''%s%s=%s''' %("sdic",obj,svalue)
            exec(scmd)
        except Exception,e:
            raise Exception("error cmd,%s" %scmd)

    return sdic

def rh_type(data):
    return type(data)

def rh_replace_data(data):
    data = str(data).strip().replace("\n","").replace("”","\"").replace("‘","\'").replace("’","\'").replace("；",";").decode("utf-8")
    if data.endswith(";"):
        data = data[:-1]
    return data.split(";")

def rh_check_result(exceldata,sdic):
        i = str(exceldata).strip().replace("\n","").replace("”","\"").replace("‘","\'").replace("’","\'").replace("；",";")
        if ":=" not in i:
            return"input data found error： %s" %i
        sname = i.split(":=")[0].strip()
        svalue = get_var(str(i.split(":=")[1]).strip())
        obj = scmd = realval =""
        for i in sname.split("."):
            if is_numeric(i):
                obj = "%s[%s]" %(obj,i)
            else:
                obj = "%s['%s']" %(obj,i)
        scmd = "%s%s" %("sdic",obj)
        try:
            realval = eval(scmd)
        except:
            return"[Failed]:cmd change error,eval(%s)" %scmd
        svalue = str(svalue).decode("utf-8")
        realval = str(realval).decode("utf-8")
        if str(svalue.replace("true", "True").replace("false", "False")).strip() == str(realval.replace("true", "True").replace("false", "False")).strip():
            pass
        elif svalue == "不为空":
            if realval == "{}" or realval == "[]":
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
            else:
                return "[success]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif svalue == "不为0":
            if realval == "0":
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
            else:
                return "[success]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif svalue == "为空":
            if realval == "{}" or realval == "[]"or realval == '':
                return"[success]:%s expect is %s,real is %s." %(sname,svalue,realval)
            else:
                return "[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif svalue == "为0":
            if realval == "0":
                return"[success]:%s expect is %s,real is %s." %(sname,svalue,realval)
            else:
                return "[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
                
        #添加INCLUDE 和EXCEPT结果验证，判断string 中是否存在要查找的关键字
        #示范：resData:=网销保费超过20万元，规则检查不通过<INCLUDE>
        #示范：resData:=投保失败，请重试<EXCEPT>
        elif "<INCLUDE>" in svalue:
            svalue = svalue.split("<")[0]
            if str(svalue) in realval:
                return "[success]:%s expect is %s,real is %s."%(sname,svalue,realval)
            else:
                return "[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif "<EXCEPT>" in svalue:
            svalue = svalue.split("<")[0]
            if str(svalue) in realval:
                return "[Failed]:%s expect is %s,real is %s."%(sname,svalue,realval)
            else:
                return "[success]:%s expect is %s,real is %s." %(sname,svalue,realval)

        elif ".00" in str(realval):
            if str(svalue) == str(realval[:-3]):
                pass
            else:
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif str(realval) == '0.0':
            if str(svalue) in ["0.0","0.00"]:
                pass
            else:
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        elif str(svalue) == "null":
            if realval == None:
                pass
            else:
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        else:
            if str(svalue) == "" and (realval == "[]" or realval == "{}"):
                pass
            else:
                return"[Failed]:%s expect is %s,real is %s." %(sname,svalue,realval)
        return "[success]:%s expect is %s,real is %s." %(sname,svalue,realval)
    
def rh_load_default_dic(file,section,option):
    config = ConfigParser.ConfigParser()
    config.readfp(open(file))
    default_dic = config.get(section,option)
    uni_default_dic=unicode_dic(default_dic)
    return uni_default_dic

def unicode_dic(data):
    if type(data)==str:
        try:
            data = eval(data)
        except:
            raise Exception("error")
    for k, v in data.iteritems():
        if type(v) == dict:
            unicode_dic(v)
        elif type(v) == list:
            for i,j in enumerate(v):
                if type(j)==str and j!='':
                    v[i]=unicode(j)
                elif type(j)==dict:
                    unicode_dic(j)
        elif type(v) == str and v!='':
            data[k] = unicode(v)
    return data

def rh_load_default_api_dic(name,file,section,option):
    config = ConfigParser.ConfigParser()
    config.readfp(open(file))
    default_dic = config.get(section,option)
    dict_name ={}
    try:
        dict_name=eval(default_dic)[name]
    except:
        raise Exception("get default dic %s,%s,%s,%s format error " %(name,file,section,option))
    finally:
        return dict_name

def rh_dic(sdic,sname):
    return sdic[sname]

def rh_dic_haskey(sdic,key):
    if type(sdic) != dict:
        raise Exception("not dic,%s" %sdic)
    if sdic.has_key(key):
        return True
    else:
        return False

def rh_replace_config_dic(sdata,argDic,resDic):
    if ":" in sdata:
        aa = sdata.split(":")
        name = aa[0]
        sval = aa[1]
        if "|" in sval:
            ssval = sval.split("|")
            for i in ssval:
                if rh_dic_haskey(resDic,i):
                    argDic[i] = resDic[i]
        else:
            if rh_dic_haskey(resDic,sval):
                    argDic[sval] = resDic[sval]

def rh_get_api_name(sdata):
    if ":" in sdata:
        return sdata.split(":")[0]
    else:
        return sdata
                    
def rh_replace_arg_dic(new_dic,add_dic):
    """将新值new_dic全部添加到add_dic中去"""
    for i in new_dic.keys():
        add_dic[i] = new_dic[i]

def rh_tuple_to_dic(res_tuple):
    l = eval(res_tuple)
    new_dic={}
    for k,v in l:
        if k=='message':
            new_dic[k.encode('utf-8')] = eval(v)
        else:
            new_dic[k.encode('utf-8')] = str(v)
    return new_dic
	
def rh_list_to_dic(names,values):
	nvs = zip(names,values)
	nv_dict = dict((name,value) for name,value in nvs)
	return nv_dict

def rh_get_column_data(value,cno):
    new_list = [x[cno] for x in value]
    return new_list
        
def rh_get_out_name(sdata):
    if ":" in sdata:
        return sdata.split(":")[1]
    else:
        return 0

def rh_set_dic(sdic,skey,svalue):
    sdic[skey] = svalue
    return sdic

def json_loads(data):
    return json.loads(data)

def json_dumps(data):
    return json.dumps(data, ensure_ascii=False)


def fibo_dic(data, new_dic={}):
    if type(data)==str:
        try:
            data = eval(data)
        except:
            raise Exception("error")
    for k, v in data.iteritems():
        if type(v) == dict:
            fibo_dic(v, new_dic)
        elif type(v) == list:
            for i in v:
                fibo_dic(i, new_dic)
        else:
            try:
                if type(eval(v)) == dict:
                    fibo_dic(eval(v), new_dic)
                else:
                    new_dic[k] = v
            except:
                new_dic[k] = v
    return new_dic

def get_csv_by_no(file, no):
    sdic = {}
    try:
        if os.path.exists(file):
            csvFile = codecs.open(file, 'r')
            reader = csv.DictReader(csvFile)
            if ',' in str(no):
                nolist = no.split(",")
                infolist = []
                for i, rows in enumerate(reader):
                    for nos in nolist:
                        if nos!=""and i == int(nos) - 1:
                            infodic = eval(str(rows).decode('gb2312').encode('utf-8'))
                            for item in rows.items():
                                key = item[0]
                                value = item[1]
                                if isinstance(value,str):
                                    if "val" in file:
                                        # 随机变量替换
                                        try:
                                            infodic[key] = get_var(unicode(value.strip()))
                                        except:
                                            infodic[key] = get_var(value.strip().decode('gb2312').encode('utf-8'))
                                    else:
                                        try:
                                            infodic[key] = unicode(value.strip())
                                        except:
                                            infodic[key] = value.strip().decode('gb2312').encode('utf-8')
                            infolist.append(infodic)
                sdic["list"]=infolist
            else:
                for i, rows in enumerate(reader):
                    if i == int(no) - 1:
                        # sdic = rows
                        sdic = eval(str(rows).decode('gb2312').encode('utf-8'))
                        for item in rows.items():
                            key=item[0]
                            value=item[1]
                            if ';' in value:
                                valuelist=value.split(';')
                                sdic[key]=valuelist
                            else:
                                if isinstance(value,str):
                                    if "val" in file:
                                        # 随机变量替换
                                        try:
                                            sdic[key] = get_var(unicode(value.strip()))
                                        except:
                                            sdic[key] = get_var(value.strip().decode('gb2312').encode('utf-8'))

                                    else:
                                        try:
                                            sdic[key] = unicode(value.strip())
                                        except:
                                            sdic[key] = value.strip().decode('gb2312').encode('utf-8')
            csvFile.close()
    except Exception, msg:
        print str(msg)
    finally:
        return sdic

def write_csv(file,row_no,col_name,col_value):
    try:
        if os.path.exists(file):
            csvFile = codecs.open(file, 'r')
            reader = csv.DictReader(csvFile)
            csv_rows=[]
            for i, row in enumerate(reader):
                sdic = row
                if i == int(row_no)-1:
                    sdic[col_name]=col_value
                csv_rows.append(sdic)
            csvFile.close()

            csvFile = codecs.open(file, 'wb')
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(csv_rows[0].keys())
            for csv_row in csv_rows:
                csvWriter.writerow(csv_row.values())
            csvFile.close()
            print "write_csv"+file
    except Exception, msg:
        print str(msg)

def write_txt(file,value):
    try:
        f=open(file,'a')
        f.write(value+'\n')
        f.close()
    except Exception, msg:
        print str(msg)

def get_arg_len(*kwargs):
    return len(kwargs)

def split_input_arg(data):
    data = data.split(":")
    return data[0],data[1]

def get_driver(browser="chrome",arg=''):
    if browser == "chrome":
        option = webdriver.ChromeOptions()
        if arg!='':
            option.add_argument(arg)
        return webdriver.Chrome(chrome_options=option)
    elif browser == "firefox":
        return webdriver.Firefox()
    elif browser == "IE":
        return webdriver.Ie()
    return webdriver.Chrome()

def quit_driver(driver):
    if driver is None:
        print "warnning::driver allready quit!"
    else:
        driver.quit()

def refresh_driver(driver):
    driver.Refresh()

def get_date(delta=0, fomat="%Y-%m-%d"):
    date_delta = (datetime.now()+ timedelta(days=delta)).strftime(fomat)
    return date_delta

def generate_applyno():
    sql = "select nbucde.l_uw_bia_interface.get_dummy_apply_bar_code('02','01') as applyno from dual"
    default_dic = EnvSetting.ENV_DEF_DIC
    sqlobj = RHOracle(usr=default_dic.get("db_bia_usr"), ip=default_dic.get("db_ip"))
    result = sqlobj.fetchone_query(sql)[0]
    return result

def get_idcard_by_day(sval,fomats="%Y%m%d"):
    stype =""
    delta = sval.split("today")[1][:sval.split("today")[1].find(",")]
    if delta == "":
        delta = 0
    id_list = sval.replace(" ", "").split(",")
    if "*" in sval:
        stype = id_list[2].split("*")[0]
        if ")" in stype:
            stype = stype[:-1]
    else:
        stype = id_list[2][:-1]
    sval = generate_id(bir=get_date(int(delta), fomat=fomats), sex=id_list[1], idtype=stype)
    return sval

def generate_idcard(sval):
    if "(" in sval:
        if "today" in sval:
            sval = get_idcard_by_day(sval)
        elif "-" in sval:
            id_list = sval[sval.index('(') + 1:sval.index(')')].replace(" ", "").split("-")
            sval = generate_id(bir=id_list[0], sex=id_list[1], idtype=id_list[2])
        else:
            id_list = sval[sval.index('(') + 1:sval.index(')')].replace(" ", "").split(",")
            sval = generate_id(bir=id_list[0], sex=id_list[1], idtype=id_list[2])
    else:
        sval = generate_id(bir='19660327', sex='2')
    return sval

def generate_today(sval):
    if "(" in sval:
        # sval='$today$-1(%Y-%m-%d)'
        fomats = sval[sval.find('(') + 1:-1]
        delta = sval.split('(%s)' % fomats)[0].split("$today$")[1]
    else:
        # sval = '$today$-1'
        fomats = "%Y%m%d"
        delta = sval.split("$today$")[1]
    if delta == "":
        delta = 0
    sval = get_date(int(delta), fomat=fomats)
    return sval

# eval()方法二次封装
def eval_str(str_data):
    # eval()对特殊值处理
    null = ""
    true = True
    false = False
    return eval(str_data)

def gen_model(sval, re):
    if Settings.CASE_GEN_DIC.get(re) is None:
        Settings.CASE_GEN_DIC[re] = sval
    else:
        sval = Settings.CASE_GEN_DIC.get(re)
    return sval

def generate_no(sval):
    if "(" in sval:
        no_list = sval[sval.index('(') + 1:sval.index(')')].replace(" ", "").split(",")
        sval = get_no(int(no_list[0]), no_list[1])
    else:
        sval = get_no()
    return sval

def generate_addr():
    sval = generate_name() + generate_name() + generate_name() + "-招商金科自动化测试-" + str(get_gendercode_by_id(generate_id(bir='', sex='3', idtype='01')))
    return sval

def generate_apply_barcode(sval):
    bar_tag = False
    if '[' in sval:
        bar_tag = True
        sval = sval[:sval.find('[')]

    if "(" in sval:
        if ',' in sval:
            doctype = sval[sval.find('(') + 1:sval.find(',')]
            version = sval[sval.find(',') + 1:sval.find(')')]
        else:
            doctype = sval[sval.find('(') + 1:-1]
            version = '01'
    else:
        doctype = '1111'
        version = '01'
    sval = get_bar_code(doctype, version)
    if bar_tag:
        sval = sval[:-2]
    return sval

def generate_sysdate(sval):
    if "(" in sval:
        extraday = sval[sval.index('(') + 1:sval.index(')')]
        sval = (date.today() + timedelta(days=int(extraday))).strftime('%Y-%m-%d')
    else:
        sval = date.today().strftime('%Y-%m-%d')
    return sval

def generate_mwxuid():
    if Settings.CASE_GEN_DIC.get("$g_wxUserId$") is None:
        raise Exception("微信ID获取失败")
    else:
        wxid = Settings.CASE_GEN_DIC.get("$g_wxUserId$")
        sval = str(md5_format(".cmrh1875", wxid))
    return sval

def get_var(sval):
    # 获取需要生成随机变量的个数flag
    g = lambda x: x in sval
    flag = sval[sval.find("*"):] if g("*") else ""
    if "$today$" in sval:
        sval = generate_today(sval)
        #sval = gen_model(res, "$today$")
    # 获取身份证  参数格式：$g_idcard$(19900101,1,01)*2,$g_idcard$(today+1,1,01)*3
    elif "$g_idcard$" in sval:
        res = generate_idcard(sval)
        sval = gen_model(res,"$g_idcard%s$" % flag)
    elif "$g_mail$" in sval:
        res = generate_mail()
        sval = gen_model(res, "$g_mail%s$" % flag)
    elif "$g_mobile$" in sval:
        res = generate_phone()
        sval = gen_model(res, "$g_mobile%s$" % flag)
    elif "$g_applyno$" in sval:
        res = generate_applyno()
        sval = gen_model(res, "$g_applyno%s$" % flag)
    elif "$g_name$" in sval:
        res = generate_name()
        sval = gen_model(res, "$g_name%s$" % flag)
    # 参数格式：$g_no$(6, "B00001")
    elif "$g_no$" in sval:
        res = generate_no(sval)
        sval = gen_model(res, "$g_no%s$" % flag)
    # 获取随机地址
    elif "$g_addrs$" in sval:
        res = generate_addr()
        sval = gen_model(res, "$g_addrs%s$" % flag)
    #获取投保单号
    elif "$g_applybarcode$" in sval:
        res = generate_apply_barcode(sval)
        sval = gen_model(res, "$g_applybarcode%s$" % flag)
    # 获取系统时间和系统时间差  参数格式：$g_sysdate$(+7)  或者 参数格式：$g_sysdate$(-7) $g_sysdate$
    elif "$g_sysdate$" in sval:
        res = generate_sysdate(sval)
        sval = gen_model(res, "$g_sysdate%s$" % flag)
    elif "$g_requestid$" in sval:
        res = get_no(11,"T","Y")
        sval = gen_model(res, "$g_requestid%s$" % flag)
    elif "$g_wxUserId$" in sval:
        res = get_no(12,"","Y")
        sval = gen_model(res, "$g_wxUserId%s$" % flag)
    elif "$g_mwxuid$" in sval:
        res = generate_mwxuid()
        sval = gen_model(res, "$g_mwxuid%s$" % flag)
    elif "$g_timestamp$" in sval:
        res = get_timestamp()
        sval = gen_model(res, "$g_timestamp%s$" % flag)
    #获取图片basse64编辑码
    elif "$g_image$" in sval:
        res = get_image_base64encode()
        sval = gen_model(res, "$g_image%s$" % flag)
    elif "$g_barcode$" in sval:
        res = get_no(5, "1211", "Y")
        sval = gen_model(res, "$g_barcode%s$" % flag)
    elif "$g_debitcard$" in sval:
        res = get_no(12, "6227007", "N")
        sval = gen_model(res, "$g_debitcard%s$" % flag)        
    elif "$g_random$" in sval:
        res = g_random(sval)
        sval = gen_model(res, "$g_random%s$" % flag)
    return sval

if __name__ == '__main__':
    # a = "$g_idcard$(19900101,1,01)"
    # print get_var(a)
    # print get_var("$g_sysdate$")
    # # print get_var("$g_idcard$")
    # print get_var("$g_requestid$")
    # print get_var("$g_wxUserId$")
    # # print get_var("$g_applyno$")
    # print get_var("$g_mwxuid$")
    # print get_var("$g_timestamp$")
    # print get_var("$g_image$")
    # print get_var("$g_idcard$(today-28,2,01)*1")
    # print get_var("$g_idcard$(today-28,2,01)*2")
    # print get_var("$g_idcard$(19900101,2,01)*1")
    # print get_var("$g_idcard$(19900101,2,01)*2")
    # print get_var("$g_idcard$*1")
    # print get_var("$g_idcard$*2")
    print get_var("$g_random$(s=T001,a=2,n=3,flag=Y)")
    print get_var("$g_random$(s=T001,a=2,n=3,flag=Y)*2")




