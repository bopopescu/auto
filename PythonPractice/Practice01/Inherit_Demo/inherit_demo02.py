# -*- coding: utf-8 -*-

# @Time    : 2018/10/8 14:40
# @Author  : songq001
# @Comment : 

"""
#新式类是指继承object的类
class A(object):
      ...........
#经典类是指没有继承object的类
class A:
     ...........
"""


# 经典类
class A:
    def __init__(self):
        print 'this is A'

    def save(self):
        print 'come from A'


class B(A):
    def __init__(self):
        print 'this is B'


class C(A):
    def __init__(self):
        print 'this is C'

    def save(self):
        print 'come from C'


class D(B, C):
    def __init__(self):
        print 'this is D'

d1 = D()
d1.save()           # 结果为'come from A   # 经典类--查找顺序:D->B->A->C->Object     找到即返回


# 新式类
class A(object):
    def __init__(self):
        print 'this is A'

    def save(self):
        print 'come from A'


class B(A):
    def __init__(self):
        print 'this is B'


class C(A):
    def __init__(self):
        print 'this is C'

    def save(self):
        print 'come from C'


class D(B, C):
    def __init__(self):
        # 重写父类构造方法
        super(D, self).__init__()
        print 'this is D'

d1 = D()
d1.save()   # 结果为'come from C'  # 新式类--查找顺序:D->B->C->A->Object
print D.__mro__


