# -*- coding: utf-8 -*-

# @Time    : 2018/9/20 0020 0:05
# @Author  : Administrator
# @Comment : 
import types

tmp_list = []


def get_target_value(key, dic):
    """
    无限遍历，python实现在多维嵌套字典、列表、元组的JSON中获取数据 （PS：若嵌套的dict里面有与外出重复的key，则只能取到最外层的key对应的value
    :param key: 目标key值
    :param dic: JSON数据
    :return: tmp_list
    tmp_list: 用于存储获取的数据, 需在方法外定义
    """
    if not isinstance(dic, dict) or not isinstance(tmp_list, list):  # 对传入数据进行格式校验
        return 'argv[1] not an dict or argv[-1] not an list '

    if key in dic.keys():
        tmp_list.append(dic[key])  # 传入数据存在则存入tmp_list
    else:
        for value in dic.values():  # 传入数据不符合则对其value值进行遍历
            if isinstance(value, dict):
                get_target_value(key, value)  # 传入数据的value值是字典，则直接调用自身
            elif isinstance(value, (list, tuple)):
                _get_value(key, value)  # 传入数据的value值是列表或者元组，则调用_get_value
    return tmp_list


def _get_value(key, val):
    for val_ in val:
        if isinstance(val_, dict):
            get_target_value(key, val_)  # 传入数据的value值是字典，则调用get_target_value
        elif isinstance(val_, (list, tuple)):
            _get_value(key, val_)   # 传入数据的value值是列表或者元组，则调用自身


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


if __name__ == '__main__':
    dict05 = {"a": 11, "b": {"kk": {"nn": 111, "a": "ppoii"}, "yy": "123aa", "uu": "777aa"},
              "c": [{"aa": 1, "bb": 2}, {"aa01": 3, "bb01": 4}, {"aa02": 5, "bb02": 6}]}

    print get_target_value("c", dict05)
    print dict_get(dict05, "c")

    lst = [1, 2, -9, 10, -2, -4, -5, -12]
    lst.sort(key=lambda x: (x < 0, abs(x)))
    print lst

