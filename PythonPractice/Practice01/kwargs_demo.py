# -*- coding: utf-8 -*-

# @Time    : 2018/9/29 14:43
# @Author  : songq001
# @Comment :

import os
from Reflection_Demo import path


class Demo01:

    def __init__(self, ip, port, token):
        self.ip = ip
        self.port = port
        self.token = token

    def print_msg(self):
        print self.ip, self.port, self.token


if __name__ == '__main__':
    STF = {"ip": "10.200.22.129", "port": "7106", "token": "70580bade44b4908ae1de4337cae4dfeebbb3cd1b11c4fa294c9ce4cc9e2b34c"}
    kkk = (1, 2, 3)
    demo = Demo01(**STF)
    demo.print_msg()

    demo01 = Demo01(*kkk)
    demo01.print_msg()

    print path

    # 输出所有文件和文件夹
    dirs = os.listdir(path)
    for file in dirs:
        print file
