# -*- coding: utf-8 -*-

# @Time    : 2018/8/28 22:56
# @Author  : Administrator
# @Comment : 

import json
import subprocess
from locust import HttpLocust, TaskSet, task

# locust -f d:/python/LocustDemo/Demo02.py --host=http://100.69.181.31


class WebsiteTasks(TaskSet):
    def on_start(self):
        pass

    @task
    def bank_card(self):
        # params = self.locust.params
        # files = self.locust.files
        files = {'image_binary': ('6230200172059037.jpg', open('C:\\pic\\6230200172059037.jpg', 'rb'), 'image/jpeg')}
        params = {"b64": "1", "recotype": "VeCard", "usernam": "test", "password": "test", "crop_image": "1"}
        with self.client.post("/ocr/v1/bank_card", data=params, files=files, catch_response=True) as response:
            print response.text
            if response.status_code == 200:
                response.success()
            else:
                response.failure('Failed!')


class FhrsTasks(TaskSet):

    headers = {"Content-Type": "application/json"}

    def on_start(self):
        login_data = {"name": "admin", "password": "123456"}
        login_data = json.dumps(login_data)
        self.client.post("/fhrs/user/login", data=login_data, headers=self.headers)

    @task
    def risk_show(self):
        data = {"companyId": "123"}
        data = json.dumps(data)
        with self.client.post("/fhrs/riskShow", data=data, headers=self.headers, catch_response=True) as response:
            # print response.text
            if response.status_code == 200:
                response.success()
            else:
                response.failure('Failed!')
                print 'Failed!'


class WebsiteUser(HttpLocust):
    # task_set = WebsiteTasks
    # host = "http://test.exocr.com:5000"
    # files = {'image_binary': open('C:\\pic\\6230200172059037.jpg', 'rb')}
    # files = {'image_binary': ('6230200172059037.jpg', open('C:\\pic\\6230200172059037.jpg', 'rb'), 'image/jpeg')}
    # data = {"b64": "1", "recotype": "VeCard", "usernam": "test", "password": "test", "crop_image": "1"}

    # =====================FhrsTasks=======================================
    task_set = FhrsTasks
    host = "http://100.69.181.31"
    min_wait = 1000
    max_wait = 3000


if __name__ == '__main__':
    subprocess.Popen('locust -f E:/work_2/git_songq/LocustDemo/Demo02.py --host=http://100.69.181.31', shell=True)


