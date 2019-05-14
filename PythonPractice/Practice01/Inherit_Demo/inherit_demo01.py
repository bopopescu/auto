# -*- coding: utf-8 -*-

# @Time    : 2018/10/8 11:01
# @Author  : songq001
# @Comment : 


class C1(object):
    def minus(self, x):
        return x / 2


class D1(C1):
    """
    MRO的方法为: 搜索算法是C3算法
    """
    def minus(self, x):
        super(D1, self).minus(x)
        print 'hello'


#
class A(object):
    def __init__(self):
        self.n = 10

    def minus(self, m):
        self.n -= m


class B(A):
    def __init__(self):
        self.n = 7

    def minus(self, m):
        super(B, self).minus(m)
        self.n -= 2

b = B()
print b.n       # b.n=7
b.minus(2)
print b.n       # b.n=3       先调A.minus --> 7-2 = 5; 在执行self.n -= 2， 5-3=3


# 多继承
class C(A):
    def __init__(self):
        # A.__init__(self)
        # super(C, self).__init__()
        self.n = 12

    def minus(self, m):
        super(C, self).minus(m)
        self.n -= 5


class D(B, C):
    def __init__(self):
        self.n = 15

    def minus(self, m):
        super(D, self).minus(m)
        self.n -= 2

d = D()
print d.n
d.minus(2)
print d.n

# 继承执行顺序    D->B->C->A->object
print D.__mro__


