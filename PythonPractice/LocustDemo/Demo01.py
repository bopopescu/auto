# -*- coding: utf-8 -*-

# @Time    : 2018/8/28 22:56
# @Author  : Administrator
# @Comment : 

import random
import Queue
from locust import HttpLocust, TaskSet, task


# 方式1       非顺序执行， 随机执行
def login(l):
    l.client.post("/login", {
        "username": "test",
        "password": "123456"
    })


def index(l):
    l.client.get("/")


def about(l):
    l.client.get("/about/")


class UserBehavior(TaskSet):                # 定义测试用户
    tasks = {index: 2, about: 1}

    def on_start(self):
        login(self)


# 方式2       顺序执行
class WebsiteTasks(TaskSet):
    def on_start(self):
        self.client.post("/login", {
            "username": "test",
            "password": "123456"
        })

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def about(self):
        self.client.get("/about/")


# 参数化示例
class UserBehavior01(TaskSet):

    def on_start(self):
        pass

    # 自定义函数参数化
    @staticmethod
    def login_user():
        users = {"user1": 123456, "user2": 123123, "user3": 111222}
        data = random.randint(1, 3)
        username = "user"+str(data)
        password = users[username]
        return username, password

    @task
    def login(self):
        username, password = UserBehavior01.login_user()
        param = {"username": username, "password": password}
        print param
        self.client.post("/login_action", data=param)


# 参数化示例2
class UserBehavior02(TaskSet):
    def on_start(self):
        pass

    # 自定义函数
    @staticmethod
    def param_pre():
        queue = Queue.Queue()
        for i in range(100):
            data = {
                "username": "test%d" % i,
                "password": "pwd%d" % i,
                "email": "test%d@xxx.com" % i,
                "phone": "135%08d" % i,
            }
            queue.put(data)
        return queue

    @task
    def login(self):
        data01 = {}
        queuedata = UserBehavior02.param_pre()
        try:
            data01 = queuedata.get()
            print data01
            # 若需要循环服用,在put即可
            # queuedata.put_nowait(data01)
        except queue.empty():
            print "no data exit!"
            exit(0)
        param = {"username": data01["username"], "password": data01["password"]}
        self.client.post("/login_action", data=param)


class WebsiteUser(HttpLocust):              # 定义模拟用户
    # task_set = UserBehavior               # 运行哪一个测试类
    task_set = WebsiteTasks
    host = "http://debugtalk.com"
    min_wait = 1000
    max_wait = 5000


if __name__ == '__main__':
        queue = Queue.Queue()
        for i in range(100):
            data = {
                "username": "test%d" % i,
                "password": "pwd%d" % i,
                "email": "test%d@xxx.com" % i,
                "phone": "135%08d" % i,
            }
            queue.put(data)
        print queue.get(99)
        print queue.get(8)

