# -*- coding: utf-8 -*-

# @Time    : 2018/9/17 0017 23:35
# @Author  : Administrator
# @Comment : 

import types


key_list = []

def get_dict_allkeys(dict_a):
    """
    多维/嵌套字典数据无限遍历
    :param dict_a: 
    :return: key_list
    """
    if isinstance(dict_a, dict):         # 使用isinstance检测数据类型
        for x in range(len(dict_a)):
            temp_key = dict_a.keys()[x]
            temp_value = dict_a[temp_key]
            print"%s : %s" % (temp_key, temp_value)
            key_list.append(temp_key)
            get_dict_allkeys(temp_value)    # 自我调用实现无限遍历
    elif isinstance(dict_a, list):
        for k in dict_a:
            if isinstance(k, dict):
                for x in range(len(k)):
                    temp_key = k.keys()[x]
                    temp_value = k[temp_key]
                    print"%s : %s" % (temp_key, temp_value)
                    key_list.append(temp_key)
                    get_dict_allkeys(temp_value)
    return key_list


def get_format_dict(dictdata):
    for (k, v) in dictdata.items():
        if isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    new_dict = i.copy()
                    dictdata = dict(dictdata.items() + new_dict.items())
            dictdata.pop(k)
            # if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
            #     return dictdata
            # else:
            #     return get_format_dict(dictdata)
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


def get_format_dict_keys(dictdata):
    list01 = dictdata.keys()
    for (k, v) in dictdata.items():
        if isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    new_dict = i.copy()
                    dictdata = dict(dictdata.items() + new_dict.items())
            dictdata.pop(k)
            # if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
            #     return dictdata
            # else:
            #     return get_format_dict_keys(dictdata)
        else:
            if isinstance(v, dict):
                new_dict = v.copy()
                dictdata.pop(k)
                dictdata = dict(dictdata.items() + new_dict.items())
                if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                    return dictdata.keys()+list01
                else:
                    return get_format_dict_keys(dictdata)
    return dictdata.keys()


def get_dict_keys(dictdata):
    return list(set(dictdata.keys()+get_format_dict_keys(dictdata)))


def get_target_value(key, dic, tmp_list):
    """     
    无限遍历，python实现在多维嵌套字典、列表、元组的JSON中获取数据 (通过两个函数循  递归  环相互调用的方法来解决这个问题)
    :param key: 目标key值
    :param dic: JSON数据
    :param tmp_list: 用于存储获取的数据
    :return: list
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():
        tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    else:
        for value in dic.values():  # 传入数据不符合则对其value值进行遍历
            if isinstance(value, dict):
                get_target_value(key, value, tmp_list)  # 传入数据的value值是字典，则直接调用自身
            elif isinstance(value, (list, tuple)):
                _get_value(key, value, tmp_list)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list


def _get_value(key, val, tmp_list):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_, tmp_list)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_, tmp_list)   # 传入数据的value值是列表或者元组，则调用自身


if __name__ == '__main__':
    dict01 = {"a": 1, "b": {"kk": {"nn": 111, "pp": "ppoii"}, "yy": "123aa", "uu": "777aa"},
              "c": [{"a": 1, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}]}
    dict02 = {"a": 1, "b": 33333, "c": [{"a": {"mm": "mm02"}, "b": 2}, {"a": 3, "b": 4}, {"a": 5, "b": 6}]}
    dict05 = {"a": 11, "b": {"kk": {"nn": 111, "pp": "ppoii"}, "yy": "123aa", "uu": "777aa"},
              "c": [{"aa": 1, "bb": 2}, {"aa01": 3, "bb01": 4}, {"aa02": 5, "bb02": 6}]}
    dict06 = {"nn": 111, "pp": "ppoii"}
    dict07 = {"nn": 222, "pp01": "ppoii"}
    # print dict(dict06.items()+dict07.items())
    print get_format_dict_keys(dict05)
    list_end = dict05.keys() + get_format_dict_keys(dict05)
    ids = list(set(list_end))
    print ids
    print get_dict_keys(dict05)
    # print get_format_dict(dict06)

    print get_format_dict(dict01)
    print get_format_dict(dict02)
    print get_dict_keys(dict02)

    ids01 = [1, 4, 3, 3, 4, 2, 3, 4, 5, 6, 1]
    ids01.sort()
    vvv = sorted(ids01)
    print ids01
    print vvv

    ids01.reverse()
    print ids01
    yyy = reversed(ids01)
    for kk in yyy:
        print kk,
    print

    # list  去重，不改变顺序
    list2 = []
    # list1 = [1, 2, 3, 2, 2, 2, 4, 6, 5]
    list1 = [1, 4, 3, 3, 4, 2, 3, 4, 5, 6, 1]
    for i in list1:
        if i not in list2:
            list2.append(i)
    print list2

    # list  顺序会改变
    ids02 = [1, 4, 3, 3, 4, 2, 3, 4, 5, 6, 1]
    ids03 = list(set(ids02))
    print ids03

    dict100 = {"isRulePass": "Y", "flag": "Y", "applyBarCode": "1186020005444120", "sumPrem": 43099, "isHighPart": "N", "productList": [{"unit": 0, "productCode": "1020", "productLevel": "1", "addPrem": 0, "productSeq": 1, "isPrimaryPlan": "Y", "prem": 43099, "amnt": 7000}]}
    print get_dict_allkeys(dict100)

