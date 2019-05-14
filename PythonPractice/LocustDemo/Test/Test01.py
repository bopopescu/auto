# -*- coding: utf-8 -*-

# @Time    : 2018/8/30 19:17
# @Author  : songq001
# @Comment : 

import requests
import json

session = requests.session()


def http_post(host, url, params, files={}, headers={}, cookies={}):

    with session.post(host + url, data=params, files=files, headers=headers, cookies=cookies) as response:
        print response.text
        if response.status_code == 200:
            print "SUCCESS!"
        else:
            print 'Failed!'


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
    headers = {"authorization": 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJjbXRva2VuIiwiaWF0IjoxNTM5MTY2MzIwLCJzdWIiOiJ7XCJ1c2VyVHlwZVwiOlwiU0FMRVwiLFwidXNlcklkXCI6XCJMMDAwMDAwMDAxQGNtcmhhZ2VudC5jb21cIixcInRva2VuXCI6XCJBYnpDc0tKSWorRWhRYi9FL2xlWDZnPT1cIn0iLCJleHAiOjE1MzkyNTI3MjB9.dTXnBGURs2UqrvqW6y8bWe091sZbaXqfszVf47-0KRg'}
    params = {"posReqDTO": "{'acceptChannelCode':'11','applyTypeCode':'3','approvalServiceType':'1','pip23':{'clientName':'圆回了','clientNo':'C00000590661','mobileNo':'18625118431','newAccount':{'bankCode':'102','accountNo':'6218525252500000','accountNoComfirm':'6218525252500000','clientNo':'C00000590661','accountNoType':'1','provinceCode':'110000','cityCode':'110200'},'oldAccounts':[{'accountNo':'62411110000','accountNoType':null,'accountOwner':'圆回了','bankCode':'308290003011','idNo':'110103198801011022','idType':'01'}]},'policyInfoList':[{'policyNo':'P000000001199450','chargingMethod':'2','applyBarCode':'1186020001890020'}],'posType':'P','serviceItems':'23'}"}
    files = {
                'applicantFiles': open('C:\\pic\\02.jpg', 'rb'),
                # 'applicantFiles': open('C:\\pic\\02.jpg', 'rb'),
                'bankId': open('C:\\pic\\02.jpg', 'rb')
            }
    # params = json.dumps(params)
    print params
    print type(params)
    print files
    host = "https://msp-di1.dev.cmrh.com:443"
    url = "/RH_MSPSERVER/pos/controller/doPos"

    http_post(host, url, params, files, headers=headers)


