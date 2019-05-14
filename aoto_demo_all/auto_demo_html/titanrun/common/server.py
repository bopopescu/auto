# -*- coding: utf-8 -*-
# @Time    : 2018/7/31 9:25
# @File    : server.py
# @Software: PyCharm
import platform
import os
from titanrun.fixtures.staf import Staf
from titanrun.fixtures.stf_connect import DeviceApi
from titanrun.common import com
import requests
import time
from business.conf import EnvSetting


class Server(object):
    def __init__(self, stf_parms, staf_server_list, location='local'):
        self.staf = Staf()
        self.stf = DeviceApi(**stf_parms)
        self.staf_server_list = staf_server_list
        self.location = location

    def appium_server(self, port=4725, bpport=14725, ip='local'):
        cmd = "appium -a 0.0.0.0 -p {0} -bp {1} --session-override".format(port, bpport)
        # sysstr = platform.system()
        # if sysstr == "Windows":
        #     path = os.path.expanduser('~') + r"\AppData\Local\Programs\Appium\resources\app\node_modules\appium\build\lib\main.js"
        #     if os.path.exists(path):
        #         cmd = "node {0} -a 0.0.0.0 -p {1} -bp {2} --session-override".format(path, port, bpport)
        # elif sysstr == "Linux":
        #     pass
        self.staf.runRemoteCommand(cmd, ip, self.location)

    def creat_mult_server(self, num, port=4725, bpport=14725, ip='local'):
        server_list = []
        for n in range(num):
            self.appium_server(port+n, bpport+n, ip)
        time.sleep(5)
        for n in range(num):
            s = self.check_appium_alive(port+n, ip)
            server_list.append(s)
        return server_list

    def creat_distributed_server(self, mobile_list, port=4725, bpport=14725, timeout=15, start_appium='true'):
        mobiles = {}
        server_dict = {}
        if start_appium == 'true':
            self.close_all_appium_server()

        try: # 连接stf平台手机
            mobile = self.stf.get_devices()
            if mobile_list.find(',') >= 0:
                mobile_list = mobile_list.split(',')
                for n in range(len(mobile)):
                    udid = self.stf.connect(mobile_list[n])
                    mobiles[mobile_list[n]] = mobile[mobile_list[n]]
                    mobiles[mobile_list[n]]['udid'] = udid
            elif mobile_list.isdigit():
                num = 0
                for k, v in mobile.items():
                    if num >= int(mobile_list):
                        break
                    udid = self.stf.connect(k)
                    mobiles[k] = v
                    mobiles[k]['udid'] = udid
                    num += 1
            else:
                udid = self.stf.connect(mobile_list)
                mobiles[mobile_list] = mobile[mobile_list]
                mobiles[mobile_list]['udid'] = udid
        except Exception as e: # 本地找运行手机
            raise Exception('stf连接失败！', e)
            # udids = com.getPhoneSerialno()
            # for u in range(len(udids)):
            #     name = os.popen('adb -s %s shell getprop ro.product.model' % udids[u]).read().strip()
            #     mobiles[name] = {}
            #     mobiles[name]['udid'] = udids[u]
            #     mobiles[name]['deviceName'] = name
        mobile_num = len(mobiles)
        if self.location == 'remote':
            staf_list = []
            for ip in self.staf_server_list:
                if self.staf.isalive(ip):
                    staf_list.append(ip)
            m = len(staf_list)
            if mobile_num >= m:
                quot = mobile_num/m
                for n in range(m):
                    if n == m-1 and n != 0: # 最后一台启动剩余的server数量
                        single_mobiles_num = mobile_num - quot * (n-1)
                    else:
                        single_mobiles_num = quot
                    for n1 in range(single_mobiles_num): # 单台staf启动server数量
                        if start_appium == 'true':
                            self.appium_server(port+n1, bpport+n1, staf_list[n])
                        mobile = mobiles.popitem()
                        self.connect_mobile(mobile[1].get('udid'), staf_list[n])
                        server_dict[mobile[0]] = mobile[1]
                        server_dict[mobile[0]]['appium_ip'] = staf_list[n]
                        server_dict[mobile[0]]['appium_port'] = port + n1
            else:
                for m in range(len(mobiles)):
                    if start_appium == 'true':
                        self.appium_server(port + m, bpport + m, staf_list[m])
                    mobile = mobiles.popitem()
                    self.connect_mobile(mobile[1].get('udid'), staf_list[m])
                    server_dict[mobile[0]] = mobile[1]
                    server_dict[mobile[0]]['appium_ip'] = staf_list[m]
                    server_dict[mobile[0]]['appium_port'] = port + m
        elif self.location == 'local':
            for m in range(len(mobiles)):
                if start_appium == 'true':
                    self.appium_server(port + m, bpport + m)
                mobile = mobiles.popitem()
                self.connect_mobile(mobile[1].get('udid'), 'local')
                server_dict[mobile[0]] = mobile[1]
                server_dict[mobile[0]]['appium_ip'] = 'localhost'
                server_dict[mobile[0]]['appium_port'] = port + m
        for mobile in server_dict.itervalues():
            now = time.time()
            while time.time() - now < timeout:
                if self.check_appium_alive(mobile['appium_port'], mobile['appium_ip']):
                    print('appium server: {}:{} 已启动成功!'.format(mobile['appium_ip'], mobile['appium_port']))
                    break
                time.sleep(0.5)
        return server_dict

    def close_appium_server(self, ip='local'):
        sysstr = platform.system()
        if sysstr == "Windows":
            cmd = 'taskkill /T /F /IM node.exe'
        else:
            cmd = 'pkill node'
        self.staf.runRemoteCommand(cmd, ip, self.location)

    def close_all_appium_server(self):
        if self.location == 'local':
            self.close_appium_server('local')
        else:
            for l in self.staf_server_list:
                self.close_appium_server(l)

    def check_appium_alive(self, port, ip='local'):
        if ip == 'local':
            ip = '127.0.0.1'
        url = "http://{}:{}/wd/hub/status".format(ip, port)
        try:
            res = requests.get(url).content
            if "\"status\":0" in res:
                return ip, port
            else:
                return True
        except Exception as e:
            return False

    def connect_mobile(self, udid, ip):
        cmd = 'adb connect {}'.format(udid)
        self.staf.runRemoteCommand(cmd, ip, self.location)

    def disconnect_mobile(self, mobiles):
        for v in mobiles.itervalues():
            if v.get('udid'):
                if ':' in v.get('udid'): # 如果udid是ip连接的，代表是stf平台手机，测试完成后需要断开连接
                    if v.get('appium_ip') == 'localhost':
                        host = 'local'
                    else:
                        host = v.get('appium_ip')
                    self.staf.runRemoteCommand('adb disconnect %s'%v.get('udid'), host, self.location)
                    self.stf.disconnect(v.get('deviceName'))


if __name__ == "__main__":
    server = Server(EnvSetting.STF,EnvSetting.STAF_SERVER)
    # server.creat_mult_server(2)
    print server.appium_server(ip='10.200.16.253')