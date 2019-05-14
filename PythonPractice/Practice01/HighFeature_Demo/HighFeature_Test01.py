# coding: utf-8

"""
python高级特性
"""

""""
1、集合的推导式
列表推导式，使用一句表达式构造一个新列表，可包含过滤、转换等操作。
语法：[exp for item in collection if codition]
"""

result1 = [i for i in range(100) if i % 3 == 0]
print result1

str_list = ["i", "love", "python"]
result2 = [i.title() for i in str_list if len(i) > 1]
print result2


"""
字典推导式，使用一句表达式构造一个新字典，可包含过滤、转换等操作。
语法：{key_exp：value_exp for item in collection if codition}
"""

dict1 = {key: value for key, value in enumerate(reversed(range(50))) if value % 7 == 0}
print dict1


"""
集合推导式
语法：{exp for item in collection if codition}
"""
set1 = {i for i in range(10)}
print set1
# 等价于
print set(range(10))


"""
嵌套列表推导式
"""
lists = [range(10), range(10, 20)]
evens = [item for ls in lists for item in ls if item % 3 == 0]
print evens


"""
多函数模式
函数列表，python中一切皆对象。
"""
# 处理字符串
str_lst = ['$1.123', '  $1123.454', '$899.12312']


def remove_space(str):
    """
    remove space
    """
    str_no_space = str.replace(' ', '')
    return str_no_space


def remove_dollar(str):
    """
    remove $
    """
    if '$' in str:
        return str.replace('$', '')
    else:
        return str


def clean_str_lst(str_lst, operations):
    """
        clean string list
    """
    result = []
    for item in str_lst:
        for op in operations:
            item = op(item)
        result.append(item)
    return result


clean_operations = [remove_space, remove_dollar]
result = clean_str_lst(str_lst, clean_operations)
print result


# 映射序列
old_list = [1, 4, 5, 7, 88]
doubled_list = map(lambda x: x * 2, old_list)
print doubled_list

a = [4, 3, 2, 5, 1]
for k in enumerate(a):
    print k,

print
b = {"a": {"c": 111}, "b": {"c": 2222}}
print b

