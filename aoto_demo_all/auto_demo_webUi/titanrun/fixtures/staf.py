# -*- coding: utf-8 -*-
# @Time    : 2018/7/30 13:55
# @File    : staf.py
# @Software: PyCharm

from PySTAF import STAFHandle
from PySTAF import STAFException
from PySTAFMon import *
import subprocess
import os


class Staf(object):

    def __init__(self):
        try:
            self.handle = STAFHandle("MyTest")
        except STAFException, e:
            print("Error registering with STAF, RC: %d" % e.rc)

    def __del__(self):
        self.unregister()

    def runRemoteCommand(self, cmd, ip='local', location='local'):
        if location == 'remote':
            print 'submit cmd:\"{}\"'.format(cmd),
            try:
                result = self.handle.submit(ip, "PROCESS", "start command {}".format(cmd))
                print("SERVER: %s, RC: %d, Result: %s" % (ip, result.rc, result.result))
            except AttributeError as e:
                raise Exception(u'SERVER: {} not start STAF !!!'.format(ip))
        elif location == 'local':
            subprocess.Popen(cmd, shell=True)

    def isalive(self, ip):
        result = self.handle.submit(ip, 'PING', 'PING')
        if result.rc == 0:
            return True
        else:
            return False

    def unregister(self):
        try:
            print('unregister staf !')
            self.handle.unregister()
        except Exception as e:
            pass

    def getmonitor(self, ip="local"):
        monitor = STAFMonitor(self.handle, ip)
        result = monitor.log("Beginning test")
        return result.rc, result.result


if __name__ == "__main__":
    staf = Staf()



