# -*- coding: utf-8 -*-
# @Time    : 2018/9/17 15:20
# @File    : monkey.py
# @Software: PyCharm

import os
from adbtool import AdbTools
import re


class monkey:
    def __init__(self, device_id='', path='.'):
        self.adb = AdbTools(device_id)
        self.monkey_file = os.path.join(path, 'logs', r'{}_monkey.txt'.format(device_id))
        self.path = path

    def install_keyboard(self):
        self.adb.install(os.path.join(self.path, 'resource', 'ADBKeyBoard.apk'))
        self.adb.adb('shell ime set com.android.adbkeyboard/.AdbIME')
        print('install keyboard success')

    def run(self, package, count=20000, throttle=100):
        cmd = 'shell monkey -p %s --ignore-timeouts --ignore-crashes --monitor-native-crashes --kill-process-after-error -s 1000000  --throttle %s -v -v -v %s > %s'%(package, throttle, count, self.monkey_file)
        # flag = self.adb.is_install('com.android.adbkeyboard') # 判断是否安装了输入法
        # if not flag:
        #     self.install_keyboard()
        print self.adb.adb(cmd).read()

    def getCrashMsg(self):
        _crashM = []
        with open(self.monkey_file) as monkey_log:
            lines = monkey_log.readlines()
            for line in lines:
                if re.findall("ANR", line):
                    print("存在anr错误:" + line)
                    _crashM.append(line)
                if re.findall("CRASH", line):
                    print("存在crash错误:" + line)
                    _crashM.append(line)
                if re.findall("Exception", line):
                    print("存在crash错误:" + line)
                    _crashM.append(line)
        return _crashM