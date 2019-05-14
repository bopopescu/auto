# coding: utf-8

import Queue
import os
import platform


class Data:

    def __init__(self, day=0, month=0, year=0):
        self.day = day
        self.month = month
        self.year = year
        print day, month, year

    @classmethod            # 类方法
    def get_date(cls, date_as_string):
        day, month, year = map(int, date_as_string.split('-'))
        data1 = cls(day, month, year)
        return data1

    @staticmethod           # 静态方法
    def get_date01(date_as_string):
        day, month, year = map(int, date_as_string.split('-'))
        return day <= 31 and month <= 12 and year <= 3999


# 队列demo
def param_pre():
    queue = Queue.Queue()
    for i in range(100):
        data = {
            "username": "test%d" % i,
            "password": "pwd%d" % i,
            "email": "test%d@xxx.com" % i,
            "phone": "135%08d" % i,
        }
        queue.put_nowait(data)
        # queue.put(data)
    return queue


# test
def test01(vlist):
    index = 0
    for k in range(10):
        index = (index + 1) % len(vlist)                # 循环重复使用列表vlist里的数据
        print index


def test02(a, b):
    return a, b, a+b

if __name__ == '__main__':
    # Data.get_date("06-09-2018")
    # print Data.get_date01("56-09-2018")
    # print Data.get_date01("06-09-2018")

    queuedata = param_pre()
    print param_pre()
    for i in range(5):
        data = queuedata.get()
        print data
        # 循环复用
        queuedata.put_nowait(data)

    vlist = ["url1", "url2", "url3", "url4", "url15"]
    test01(vlist)

    print os.path.sep
    print type(os.path.sep)
    print platform.system()

    print test02(b=100, a=10)

    cul = "5*50+12348"
    a = compile(cul, "", "eval")
    print eval(a)
    print eval(cul)

    str = "for i in range(0,10): print(i)"
    c = compile(str, '', 'exec')
    exec(c)
    exec(str)



