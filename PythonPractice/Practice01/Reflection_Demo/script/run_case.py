# -*- coding: utf-8 -*-

# @Time    : 2018/9/29 9:13
# @Author  : songq001
# @Comment : 


class Test01:

    def __init__(self, a=0, b=0):
        self.a = a
        self.b = b

    def add(self, n):
        return self.a + self.b + n

    def factorial(self, n):
        if n == 0:
            return 1
        else:
            return n*self.factorial(n-1)


# test01 = Test01(1, 100)
# print test01.add()
# print test01.factorial(5)
#
# tDict = {}.fromkeys(range(10), ["A", "B"])
# print tDict

