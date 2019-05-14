# -*- coding: utf-8 -*-

# @Time    : 2018/10/12 16:08
# @Author  : songq001
# @Comment :

import types
import json


# eval()方法二次封装
def eval_str(str_data):
    # eval()对特殊值处理
    null = ""
    true = True
    false = False
    return eval(str_data)


def is_numeric(s):
    if s.startswith("-") or s.startswith("+") or "." in s:
        return all(c in "0123456789.+-" for c in s)
    else:
        return all(c in "0123456789" for c in s)


# 获取复杂嵌套list，json对应的下标（key）值, 可以去到任意值
# 格式：keytag： "2.a"      dict_data：[{"a": "111", "b": 222}, "bbbb", {"a": "555", "b": 222}]
def get_nestdict_value(keytag, dict_data):
    if type(dict_data) not in [types.ListType, types.DictType]:
        # dict_data = json.loads(dict_data)
        dict_data = eval_str(dict_data)  # 效果同上
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
    except Exception, e:
        print e.message
        return "[Failed]:cmd change error,eval(%s)" % scmd
    return realval


def my_t_01():
    json_t = [{"is_deleted": 0, "subnet_id": None,
               "vpc_info": {"zone_id": "1", "tenant_id": "a7ee782a867c4447b5628a597b165436", "public": True,
                            "project": {"updated_date": "2018-09-14 15:32:34", "status": "active", "is_deleted": 0,
                                        "name": "auto_test", "update_openstack_flag": None,
                                        "tenant_id": "a7ee782a867c4447b5628a597b165436", "enabled": True,
                                        "create_security_group_flag": True, "created_date": "2018-09-14 15:32:31",
                                        "deleted_date": None, "create_openstack_flag": True,
                                        "id": "7c6e89dac1964d79ada8665c5b915c52", "desc": "Auto_自动化测试数据，勿动"},
                            "state": "up", "created_date": "2018-09-14 16:03:01", "cidr": "100.69.4.0/24",
                            "project_id": "7c6e89dac1964d79ada8665c5b915c52", "id": "7cd61f81167f4af4867adca0cfcee0bd",
                            "tenant": {"updated_date": "2018-09-14 15:31:03", "is_deleted": 0, "name": "test",
                                       "enabled": True, "created_date": "2018-09-14 15:30:47",
                                       "desc": "Auto_云管自动化脚本数据，勿动", "id": "a7ee782a867c4447b5628a597b165436",
                                       "cmdb_tenant_id": "ch"}, "name": "auto_test_slave"},
               "service_ip": "100.69.4.106", "service_id": "832adc597b1b4051812501edbc7ee6f1",
               "vpc_id": "7cd61f81167f4af4867adca0cfcee0bd", "id": "0ffb8963c3114ec18ab4794ffb485eda"}]
    json_t = eval(str(json_t).strip())
    print type(json_t) in [types.ListType, types.DictType]
    print json_t
    print get_nestdict_value("0.id", json_t)
    print json_t[0]["id"]

def my_t_02():
    """
    关于python2中的unicode和str以及python3中的str和bytes
    https://www.cnblogs.com/yangmingxianshen/p/7990102.html
    :return: 
    """
    my_bytes = 'byte类型'
    print type(my_bytes)
    # str to bytes
    # my_bytes_02 = my_bytes.encode('utf-8')      # 通过encode()把str转成byte  注：python3中的方法， python2报错
    # my_bytes_02 = bytes(my_bytes, encoding='utf8')  # 效果同上    注：python3中的方法， python2报错
    # print type(my_bytes_02)

    # bytes to str
    # my_bytes_03 = my_bytes_02.decode('utf-8')
    # my_bytes_03 = str(my_bytes_02, encoding="utf-8")

    my_bytes_00 = unicode(my_bytes, encoding='utf-8')
    my_bytes_001 = my_bytes.decode('utf-8')             # 效果同上
    print type(my_bytes_00)
    print type(my_bytes_001)
    print type(u'byte类型')
    print my_bytes
    print u'byte类型'


if __name__ == '__main__':
        pass
        my_t_02()


