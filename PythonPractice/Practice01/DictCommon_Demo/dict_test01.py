# -*- coding: utf-8 -*-

# @Time    : 2018/10/3 0003 2:34
# @Author  : Administrator
# @Comment : 


"""
传入一个Json串，返回一个字典，字典只取出Json最底层的数据，中间如果有字典形式的字符串也需要进行处理，请以下面数据为例。
输入:
Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]}
输出：
Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
"""

import types
import time
import datetime
import sys
import json
import random
from datetime import date
import string

sys.setrecursionlimit(20000)

# json合并    嵌套的json取内值合并成一个
# Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]} 输出： Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
# def get_format_dict(dictdata):
#     if "{" in str(dictdata)[1:-1] or "}" in str(dictdata)[1:-1]:
#         for k in dictdata.keys():
#             # if str(dictdata[k]).startswith("{"):
#             if isinstance(dictdata[k], dict):
#                 new_dict = dictdata[k].copy()
#                 dictdata.pop(k)
#                 dictdata = dict(dictdata, **new_dict)
#         return get_format_dict(dictdata)
#     return dictdata


# def get_format_dict(dictdata):
#     for (k, v) in dictdata.items():
#         if isinstance(v, dict):
#             new_dict = v.copy()
#             dictdata.pop(k)
#             dictdata = dict(dictdata.items() + new_dict.items())
#             if "{" in str(dictdata)[1:-1] or "}" in str(dictdata)[1:-1]:
#                 return get_format_dict(dictdata)
#     return dictdata


# json合并    嵌套的json取内值合并成一个
# Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]} 输出： Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
def get_format_dict(dictdata):
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
                return get_format_dict(dictdata)
        else:
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
    return default


# 获取字典中的objkey对应的值，适用于字典嵌套
# dict:字典
# objkey:目标key
# default:找不到时返回的默认值
def dict_get02(dict, objkey, default=None):
    tmp = dict
    for k, v in tmp.items():
        if k == objkey:
            return v
        else:
            if type(v) is types.DictType:
                ret = dict_get02(v, objkey, default)
                if ret is not default:
                    return ret
            elif type(v) is types.ListType:
                for val in v:
                    ret = dict_get02(val, objkey, default)
                    if ret is not default:
                        return ret
    return default


# 获取字典中的objkey对应的值，适用于字典嵌套
# dict:字典
# objkey:目标key
# default:找不到时返回的默认值
# PS:若嵌套的json或者list中有key名称相同，则只能获取到第一个key的值，故只能取第一个key做对比
def dict_get03(dict, objkey, default=None):
    tmp = dict
    for k, v in tmp.items():
        if k == objkey:
            if type(v) is types.DictType:
                ret = dict_get(v, objkey, default)
                if ret is not default:
                    return ret
            elif type(v) is types.ListType:
                for val in v:
                    ret = dict_get(val, objkey, default)
                    if ret is not default:
                        return ret
            else:
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


# 查找嵌套list
def list_get(vlist, objkey, default=None):
    tmp = vlist
    for i in tmp:
        if i == objkey:
            return i
        else:
            if type(i) is types.ListType:
                ret = list_get(i, objkey, default=None)
                if ret is not default:
                    return ret
    return default


def list_get02(list, key):
    tmp = list
    for i in tmp:
        if key == i:
            return i


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


if __name__ == '__main__':

    print "================================"
    dict01 = {"a": "aa", "b": [{"b": "cc", "d": "dd"}, {"f": {"e": "ee"}}]}
    print get_format_dict(dict01)

    json_00 = {"row_num": 1}
    json_11 = {"data": {"row_num1": 11, "last_id2": 19111, "data0": {"row_num001": 100001}}}
    json_kk = {"status": 0, "msg": "", "data": {"data": {"row_num": 1, "last_id": 19, "data": {"row_num1": 11, "last_id2": 19111, "data0": {"row_num001": 1001}}}}}
    # print get_format_dict(json_kk)

    # print str(json_00)[1:-1]

    # print json_kk.items()
    # print json_00.items() in json_kk.items()

    # =====================
    # 如
    dicttest = {"result": {"code": {"num": "110002"}, "msg": "设备设备序列号或验证码错误"}, "status": 0}
    # ret = dict_get02(dicttest, 'msg')
    # print(ret)

    dicttest02 = {"data": { "count": 4, "data": [ { "first_name": "测试内容itdx", "group_id": 1, "last_name": "测试内容0833", "email": "admin@cmrh.com", "enabled": 1, "id": 1, "is_active": 1, "username": "admin" }, { "first_name": "测试内容itdx", "group_id": 1, "last_name": "测试内容0833", "email": "yuancz@cmrh.com", "enabled": 1, "id": 3, "is_active": 1, "username": "yuancz" }, { "first_name": "测试内容itdx", "group_id": 1, "last_name": "测试内容0833", "email": "fengjy001@cmrh.com", "enabled": 1, "id": 4, "is_active": 1, "username": "fengjy001" }, { "first_name": "测试内容itdx", "group_id": 1, "last_name": "测试内容0833", "email": "zhangrd001@cmrh.com", "enabled": 1, "id": 5, "is_active": 1, "username": "zhangrd001" } ] }, "msg": 1, "status": 0 }
    ret = dict_get02(dicttest02, 'id')
    print(ret)

    list_01 = [[1, [2, 555, 10000]], 3, 100]
    # print list_get(list_01, 10000)
    # list_01.remove(2)
    # print list_01

    list_01 = [9999, 3, 100]
    print list_get02(list_01, 3)

    # 获取日期
    print time.strftime("%Y-%m-%d", time.localtime())
    print datetime.date.today() + datetime.timedelta(days=-7)
    print datetime.date.today()


    print "error after %s, %s" % ("ppppp", "fdsfsdf")

    print "dsfsdfsdf{}11"["dsfsdfsdf{}11".find("{"):-2]

    sval = "$g_no$(6, \"B00001\")"
    no_list = sval[sval.index('(') + 1:sval.index(')')].replace(" ", "").split(",")
    print int(no_list[0])

    print "".join(random.choice("0123456789") for i in range(8))
    print "".join(str(random.choice(range(10))) for i in range(8))

    print "".join(random.sample(['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 10)).replace(' ', '')

    print isinstance(date.today(), date)
    print type(date.today())

    dict_01 = {"flag":"Y","applyBarInfo":"[{\"applicantNo\":\"520325196603272842\",\"applyBarCode\":\"1194010000582621\",\"insuredType\":null,\"firstPremium\":\"124182\",\"applicantName\":\"苗环越\",\"checkReason\":null,\"productName\":\"招商仁和和家盛世终身寿险B款\",\"productCode\":\"2004\",\"applicantType\":\"01\",\"totalNUM\":\"310\",\"insuredNo\":null,\"insuredName\":\"苗环越\",\"relationship\":\"01\"},{\"applicantNo\":\"610302196603271345\",\"applyBarCode\":\"1194010000584421\",\"insuredType\":null,\"firstPremium\":\"124182\",\"applicantName\":\"姜下怡\",\"checkReason\":null,\"productName\":\"招商仁和和家盛世终身寿险B款\",\"productCode\":\"2004\",\"applicantType\":\"01\",\"totalNUM\":\"310\",\"insuredNo\":null,\"insuredName\":\"姜下怡\",\"relationship\":\"01\"},{\"applicantNo\":\"65430119660327222X\",\"applyBarCode\":\"1194010000585018\",\"insuredType\":null,\"firstPremium\":\"124182\",\"applicantName\":\"柏宝国\",\"checkReason\":null,\"productName\":\"招商仁和和家盛世终身寿险B款\",\"productCode\":\"2004\",\"applicantType\":\"01\",\"totalNUM\":\"310\",\"insuredNo\":null,\"insuredName\":\"柏宝国\",\"relationship\":\"01\"},{\"applicantNo\":\"220182196603271589\",\"applyBarCode\":\"1194010000585624\",\"insuredType\":null,\"firstPremium\":\"124182\",\"applicantName\":\"毕们赫\",\"checkReason\":null,\"productName\":\"招商仁和和家盛世终身寿险B款\",\"productCode\":\"2004\",\"applicantType\":\"01\",\"totalNUM\":\"310\",\"insuredNo\":null,\"insuredName\":\"毕们赫\",\"relationship\":\"01\"},{\"applicantNo\":\"623025196603271903\",\"applyBarCode\":\"1194010000586221\",\"insuredType\":null,\"firstPremium\":\"124182\",\"applicantName\":\"皮手彬\",\"checkReason\":null,\"productName\":\"招商仁和和家盛世终身寿险B款\",\"productCode\":\"2004\",\"applicantType\":\"01\",\"totalNUM\":\"310\",\"insuredNo\":null,\"insuredName\":\"皮手彬\",\"relationship\":\"01\"}]"}
    # applyBarInfo.0.applyBarCode
    print type(dict_01)
    print eval(str(dict_01).replace("\\", ""))
    # print get_nestdict_value("applyBarInfo", eval(str(dict_01).replace("\\", "")))
    print eval_str(get_nestdict_value("applyBarInfo", dict_01))[0]

    print dict_get02(dict01, "b")

