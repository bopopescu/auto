# -*- coding: utf-8 -*-

# @Time    : 2018/8/30 19:17
# @Author  : songq001
# @Comment : 

import requests
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# 移除SSL认证，控制台输出InsecureRequestWarning。
urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()
session = requests.session()


def http_post(host, url, params, files={}, headers={}, cookies={}):
    print "请求接口：" + host + url
    # try:
    # with session.post(host + url, data=params, files=files, headers=headers, cookies=cookies, verify=False) as response:
    response = session.post(host + url, data=params, files=files, headers=headers, cookies=cookies, verify=False)
    print response.text
    if response.status_code == 200:
        print "SUCCESS!"
    else:
        print 'Failed!'
        # except Exception, e:
        #     print e.message


def login():
    headers = {"Content-Type": "application/json"}
    url = "http://100.69.181.31"
    login_data = {"name": "admin", "password": "123456"}
    login_data = json.dumps(login_data)
    with session.post(url + "/fhrs/user/login", data=login_data, headers=headers) as response:
        print response.text, response.status_code


if __name__ == '__main__':
    # bank_card
    # files = {'image_binary': ('6230200172059037.jpg', open('C:\\pic\\6230200172059037.jpg', 'rb'), 'image/jpeg')}
    # params = {"b64": "1", "recotype": "VeCard", "usernam": "test", "password": "test", "crop_image": "1"}
    # host = "http://test.exocr.com:5000"
    # url = "/ocr/v1/bank_card"

    # recognize_hukoubu
    # files = {'filename': ('02.jpg', open('C:\\pic\\02.jpg', 'rb'), 'image/jpeg')}
    # files = {'filename': open('C:\\pic\\02.jpg', 'rb')}
    # params = {}
    # host = "http://100.69.216.49:3308"
    # url = "/icr/recognize_hukoubu?owner=1"

    # fhrs
    # headers = {"Content-Type": 'application/json'}
    # params = {"name": "admin", "password": "123456"}
    # params = json.dumps(params)
    # host = "http://100.69.181.31"
    # url = "/fhrs/user/login"

    # msp
    host = "https://msp-di1.dev.cmrh.com"
    # headers = {"authorization": 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJjbXRva2VuIiwiaWF0IjoxNTM5MTcwNTkyLCJzdWIiOiJ7XCJ1c2VyVHlwZVwiOlwiU0FMRVwiLFwidXNlcklkXCI6XCJMMDAwMDAwMDAxQGNtcmhhZ2VudC5jb21cIixcInRva2VuXCI6XCJBYnpDc0tKSWorRWhRYi9FL2xlWDZnPT1cIn0iLCJleHAiOjE1MzkyNTY5OTJ9.0ONcG1jws5CJgtEwFd7h371jcFJVmUV11snMGy5AY_A'}
    # params = {"posReqDTO": "{'acceptChannelCode':'11','applyTypeCode':'3','approvalServiceType':'1','pip23':{'clientName':'圆回了','clientNo':'C00000590661','mobileNo':'18625118431','newAccount':{'bankCode':'102','accountNo':'6218525252500000','accountNoComfirm':'6218525252500000','clientNo':'C00000590661','accountNoType':'1','provinceCode':'110000','cityCode':'110200'},'oldAccounts':[{'accountNo':'62411110000','accountNoType':null,'accountOwner':'圆回了','bankCode':'308290003011','idNo':'110103198801011022','idType':'01'}]},'policyInfoList':[{'policyNo':'P000000001199450','chargingMethod':'2','applyBarCode':'1186020001890020'}],'posType':'P','serviceItems':'23'}"}
    # files = {
    #             'applicantFiles': open('C:\\pic\\02.jpg', 'rb'),
    #             # 'applicantFiles': open('C:\\pic\\02.jpg', 'rb'),
    #             'bankId': open('C:\\pic\\02.jpg', 'rb')
    #         }
    # url = "/RH_MSPSERVER/pos/controller/doPos"

    #
    # params = {"type": "2"}
    # files = {
    #             'file': open('C:\\pic\\1.jpg', 'rb'),
    #         }
    # url = "/RH_MSPSERVER/newWechat/ocr/getBankCardOrIdCardRecognize"

    # 手写签名拍照上传
    params = {"imageType": "1338", "claimSettlementId": "YSTMS021809291624367240000001143",
              "applicantId": "01d615d7-e0fb-41e0-ad71-340f93277bc0", "isFrontPage": "Y"}
    files = {
        'imageFile': open('C:\\pic\\1.jpg', 'rb'),
    }
    url = "/RH_MSPSERVER/claim/reportAccident/uploadFile"

    # params = json.dumps(params)
    print params
    print files
    headers = {}
    http_post(host, url, params, files, headers=headers)


