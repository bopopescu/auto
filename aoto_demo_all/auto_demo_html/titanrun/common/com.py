#!/usr/bin/env python
# coding=utf-8

# ****************************************************************
# com.py  
# Author     : Lieb  
# Version    : 1.0  
# Date       : 2015-1-21  
# Description: 公共函数  
# ****************************************************************

import os
import sys
import hashlib
import random
import subprocess
import time


mailtmpl = """
<html>
<body>
Hello:<br>
&nbsp;&nbsp;today: %s<br>
&nbsp;&nbsp;check: %s<br>
&nbsp;&nbsp;report:%s<br>
</body>
</html>"""


def getuser(n):
    '''n为用户名位数'''
    return "".join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', n))


def find_newfile(path):
    if os.path.isfile(path):
        return path
    else:
        lists = os.listdir(path)
        if lists:
            lists.sort(key=lambda fn: os.path.getmtime(path + os.path.sep + fn) if not os.path.isdir(
                path + os.path.sep + fn) else 0)
            file = os.path.join(path, lists[-1])
            return file


def getruntime(func):
    # 获取函数运行时间
    def check(*args, **kwargs):
        startTime = time.time()
        f = func(*args, **kwargs)
        endTime = time.time()
        print '方法:%s,耗时:%s秒' % (func.__name__, (endTime - startTime))
        return f
    return check


def failrun(n=3):
    # 失败重跑case装饰器
    def decorator(func):
        def wrapper(*args, **kw):
            for i in range(n):
                try:
                    r = func(*args, **kw)
                    return r
                except AssertionError as err:
                    print '用例第一次失败原因:%s' % err
            raise AssertionError

        return wrapper

    return decorator


def getPhoneSerialno():
    serialno = []
    p = subprocess.Popen('adb devices', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = p.stdout.readlines()
    stderr = p.stderr.readlines()
    if stderr:
        print '获取手机id错误，请查看手机是否已正确连接！'
        return
    for line in stdout:
        if line.find('\tdevice\r'):
            phoneinfo = line.split('\t')
            if len(phoneinfo) == 2:
                serialno.append(phoneinfo[0])
    return serialno


def getStatus(content):
    token1 = '<strong>Status:</strong>'
    token2 = '</p>'
    pos1 = content.find(token1) + len(token1)
    pos2 = content[pos1:].find(token2)
    status = content[pos1:pos1 + pos2]
    return status


def getmd5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()


def setdefaultcode():
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")


def getappver():
    buf = os.popen('adb shell dumpsys package com.esun.ui')
    for line in buf.readlines():
        if line.find('versionName=') != -1:
            ver = line.split('=')[1]
            return ver


def kill_appium():
    if sys.platform == "win32":
        os.system('taskkill /T /F /IM node.exe')
    else:
        os.system('pkill node')
