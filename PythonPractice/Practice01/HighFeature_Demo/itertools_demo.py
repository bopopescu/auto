# coding: utf-8


"""
itertools   迭代器模块
"""

from itertools import count
from itertools import islice
from itertools import cycle


"""
count(初值=0, 步长=1)
"""
for i in count(10, 5):
    if i > 20:
        break
    else:
        print i,

print

"""
islice 的第二个参数控制何时停止迭代
"""
for i in islice(count(10), 5):
    print(i),

print

"""
cycle(可迭代对象)    :itertools 中的 cycle 迭代器允许你创建一个能在一组值间无限循环的迭代器
"""
count = 0
for item in cycle("XYZ"):
    if count > 10:
        break
    else:
        print item,
        count += 1

polys = ['triangle', 'square', 'pentagon', 'rectangle']
iterator = cycle(polys)
print
print next(iterator)
print next(iterator)
print next(iterator)
print next(iterator)
print next(iterator)





