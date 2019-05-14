# -*- coding: utf-8 -*-

# @Time    : 2018/8/28 22:56
# @Author  : Administrator
# @Comment : 

import json
import subprocess
from locust import HttpLocust, TaskSet, task

# locust -f d:/python/LocustDemo/HeHeOrcPerformance.py --host=http://100.69.216.49:3308


class HeHeTasks(TaskSet):
    def on_start(self):
        pass

    @task
    def recognize_hukoubu(self):
        assert_text = u"名戴熙凡"
        files = {'filename': ('02.jpg', open('C:\\pic\\02.jpg', 'rb'), 'image/jpeg')}
        params = {}
        with self.client.post("/icr/recognize_hukoubu?owner=1", data=params, files=files, catch_response=True) as response:
            # print response.text
            if response.status_code == 200 and assert_text in response.text:
                response.success()
            else:
                response.failure('Failed!')


class WebsiteUser(HttpLocust):
    task_set = HeHeTasks
    host = "http://100.69.216.49:3308"
    # min_wait = 1000
    # max_wait = 3000


if __name__ == '__main__':
    subprocess.Popen('locust -f E:/work_2/git_songq/LocustDemo/Demo02.py --host=http://100.69.181.31', shell=True)


