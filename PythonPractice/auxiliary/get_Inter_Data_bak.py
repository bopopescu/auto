# -*- coding: utf-8 -*-
import os
import sys
import logging
import configparser
import json
import subprocess
import re
try:
    from urllib import unquote, urlencode
except Exception as e:
    from urllib.parse import unquote, urlencode
from mitmproxy import http
from mitmproxy import io
from mitmproxy.exceptions import FlowReadException

enable_proxy = '''@echo off 
echo 开始设置IE代理上网 
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "http={}:{};https={}:{}" /f 
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "<-loopback>" /f
'''
disable_proxy = '''@echo off 
echo 开始清除IE代理设置 
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "" /f
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /f
'''

ENV_DEFAULT_DATA = {}
QUERY_STRING = {}
DICT_IN_OUT = {}
REQUEST_METHOD = {}
MODEL_URL_DATA = {}
HOST = ["msp-di1.dev.cmrh.com", "10.62.181.161", "msp-st1.uat.cmrh.com", "100.69.181.13"]

ini_file = 'para_configuration.ini'
record_file = 'record.json'

logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
console = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return unquote(obj.decode("utf-8"))
        return json.JSONEncoder.default(self, obj)


class RHIniParser(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.add_section("DATA")
        self.config.add_section("PARA")
        self.config.add_section("METHED")
        self.config.add_section("MODEL_URL")

    def get_ini_info(self, section, option):
        return self.config.get(section, option)

    def set_ini_info(self, section, option, val):
        self.config.set(section, option, val)
        self.config.write(open(ini_file, 'w'))


def json_dump(data):
    return json.dumps(data, indent=4, cls=MyEncoder)


def record_data(url, method, header, request, response):
    flow = {}
    flow['url'] = url
    flow['method'] = method
    flow['header'] = header
    flow['request'] = request
    flow['response'] = response
    with open(record_file, 'a+') as f:
        f.write(json.dumps(flow, indent=4, cls=MyEncoder))
        f.write(',')
        f.write('\r\n')


def multipart_to_data(data):
    g = re.findall("name=\"(\S+)\"\r\n\r\n(.*)\r\n", str(data))
    s = ""
    for k, v in g:
        s += '{}={}&'.format(k.strip(), v.strip())
    return s[:-1]


class modified_proxy:
    def enable_proxy(self, ip='127.0.0.1', port='8080'):
        fil = 'enable_proxy.bat'
        with open(fil, "w") as f:
            f.write(enable_proxy.format(ip, port, ip, port))
        code = subprocess.call(fil)
        if code == 0:
            logger.info("设置代理成功")
        else:
            logger.info("设置代理失败")
        if os.path.isfile(fil):
            os.remove(fil)

    def disable_proxy(self):
        fil = 'disable_proxy.bat'
        with open(fil, "w") as f:
            f.write(disable_proxy)
        code = subprocess.call(fil)
        if code == 0:
            logger.info("取消代理成功")
        else:
            logger.info("取消代理失败")
        if os.path.isfile(fil):
            os.remove(fil)


ini = RHIniParser()


def deal_data(flow):
    if not isinstance(flow, http.HTTPFlow):
        return
    response = flow.response
    request = flow.request
    logger.debug(request)
    if "?" in request.path:
        p = request.path.split("?")
        path = p[0].split("/")
    else:
        p = None
        path = request.path.split("/")
    if request.host in HOST and len(path) > 1:
        method = request.method
        if method == "GET":
            if p:
                parm = p[1]
                inter = path[-1]
                if not inter.endswith(('js', 'ico', 'css')):
                    if inter == "SsoLogin.sso" and "RF_OP=OP_AQUIRE_TOKEN" in unquote(parm):
                        ENV_DEFAULT_DATA[inter] = {"01": unquote(parm)}
                        REQUEST_METHOD[inter] = {"01": request.method.lower()}
                        MODEL_URL_DATA[inter] = {"01": '/'.join(path[:-1]) + '/'}
                        DICT_IN_OUT[inter] = {"01": {"output": {"returnObject.RF_TOKEN": ""}}}
                    elif inter == "SsoLogin.sso" and "RF_OP=OP_SET_LOGIN" in unquote(parm):
                        ENV_DEFAULT_DATA[inter].update({"02": unquote(parm)})
                        REQUEST_METHOD[inter].update({"02": request.method.lower()})
                        MODEL_URL_DATA[inter].update({"02": '/'.join(path[:-1]) + '/'})
                        DICT_IN_OUT[inter].update({"02": {"input": {"LOGIN_INFO": "returnObject"}}})
                    elif inter == "Login.sso":
                        ENV_DEFAULT_DATA[inter] = {"01": unquote(parm)}
                        REQUEST_METHOD[inter] = {"01": request.method.lower()}
                        MODEL_URL_DATA[inter] = {"01": '/'.join(path[:-1]) + '/'}
                        DICT_IN_OUT[inter] = {"01": {"input": {"RF_TOKEN":"returnObject.RF_TOKEN"}, "output": {"returnObject":""}}}
                    else:
                        ENV_DEFAULT_DATA[inter] = unquote(parm)
                        REQUEST_METHOD[inter] = request.method.lower()
                        MODEL_URL_DATA[inter] = '/'.join(path[:-1]) + '/'

                    ini.set_ini_info("DATA", "ENV_DEFAULT_DATA", json_dump(ENV_DEFAULT_DATA))
                    try:
                        ini.set_ini_info("PARA", "DICT_IN_OUT", json_dump(DICT_IN_OUT))
                    except Exception as e:
                        logger.exception(str(e))
                    ini.set_ini_info("METHED", "REQUEST_METHOD", json_dump(REQUEST_METHOD))
                    ini.set_ini_info("MODEL_URL", "MODEL_URL_DATA", json_dump(MODEL_URL_DATA))
                    record_data(request.host+":"+str(request.port)+request.path, request.method, dict(request.headers), request.content, response.content)
        elif method == "POST":
            if p:
                parm = p[1]
                inter = path[-1]
                if not inter.endswith(('js', 'ico', 'css')):
                    QUERY_STRING[inter] = unquote(parm).encode('utf-8')
                    ENV_DEFAULT_DATA[inter] = request.content
                    # REQUEST_METHOD[inter] = request.method.lower()
                    MODEL_URL_DATA[inter] = '/'.join(path[:-1]) + '/'
                    ini.set_ini_info("DATA", "ENV_DEFAULT_DATA", json_dump(ENV_DEFAULT_DATA))
                    ini.set_ini_info("DATA", "QUERY_STRING", json_dump(QUERY_STRING))
                    ini.set_ini_info("PARA", "DICT_IN_OUT", "{}")
                    ini.set_ini_info("METHED", "REQUEST_METHOD", json_dump(REQUEST_METHOD))
                    ini.set_ini_info("MODEL_URL", "MODEL_URL_DATA", json_dump(MODEL_URL_DATA))
            elif not path[-1].endswith(('js', 'ico', 'css')):
                inter = path[-1]
                if "multipart/form-data" in dict(request.headers).get("Content-Type"):
                    content = multipart_to_data(request.text)
                    # print(content)
                    REQUEST_METHOD[inter] = 'uploadfiles'
                else:
                    content = request.content
                ENV_DEFAULT_DATA[inter] = content
                # REQUEST_METHOD[inter] = request.method.lower()
                MODEL_URL_DATA[inter] = '/'.join(path[:-1]) + '/'
                ini.set_ini_info("DATA", "ENV_DEFAULT_DATA", json_dump(ENV_DEFAULT_DATA))
                # ini.set_ini_info("PARA", "DICT_IN_OUT", "{}")
                ini.set_ini_info("METHED", "REQUEST_METHOD", json_dump(REQUEST_METHOD))
                ini.set_ini_info("MODEL_URL", "MODEL_URL_DATA", json_dump(MODEL_URL_DATA))
            record_data(request.host + ":" + str(request.port) + request.path, request.method, dict(request.headers), request.content,
                        response.content)


def main():
    try:
        # mitm_path = r'D:\Users\chenlb001\AppData\Local\Continuum\Anaconda2\envs\python36\Scripts'
        # os.environ["PATH"] = mitm_path + ";" + os.environ['PATH']
        modified_proxy().enable_proxy()
        if os.path.isfile('out'):
            os.remove('out')
        if os.path.isfile(record_file):
            os.remove(record_file)
        child =subprocess.Popen("mitmdump -w out", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        while child.poll() is None:
            # pass
            logger.info(child.stdout.readline())
        pass
    except KeyboardInterrupt as e:
        logger.warning(e)
        if os.path.isfile('out'):
            with open('out', "rb") as logfile:
                freader = io.FlowReader(logfile)
                try:
                    for f in freader.stream():
                        deal_data(f)
                    if os.path.isfile(ini_file):
                        logger.info('成功生成:' + os.getcwd()+ ini_file)
                except FlowReadException as e:
                    print("Flow file corrupted: {}".format(e))
        else:
            logger.warning('未能找到out文件')
    finally:
        child.kill()
        logger.info('关闭mitmproxy代理成功')
        modified_proxy().disable_proxy()

if __name__ == '__main__':
    main()
    # with open('out', "rb") as logfile:
    #     freader = io.FlowReader(logfile)
    #     try:
    #         for f in freader.stream():
    #             deal_data(f)
    #         logger.info('成功生成:' + os.getcwd() + ini_file)
    #     except FlowReadException as e:
    #         print("Flow file corrupted: {}".format(e))
