# -*- coding: utf-8 -*-

# @Time    : 2018/10/8 15:22
# @Author  : songq001
# @Comment : 

"""
classmethod 第一个参数永远是 cls
"""


class Date(object):
    def __init__(self, day=0, month=0, year=0):
        self.day = day
        self.month = month
        self.year = year

    @classmethod
    def from_string(cls, date_as_string):
        day, month, year = map(int, date_as_string.split('-'))
        date1 = cls(day, month, year)
        return date1


# 通过类方法构造实例
date2 = Date.from_string('11-09-2012')
print date2.day
print date2.year
print date2.month



