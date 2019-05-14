# -*- coding: utf-8 -*-

# @Time    : 2018/9/29 17:42
# @Author  : songq001
# @Comment : 

from titanrun.model.Model import Model


def web_flow_model(data_resouce, model="ride", version='', browser="chrome"):
    model = Model(data_resouce, model, version, browser)
    model.web_model()


if __name__ == '__main__':

    # demo01
    data_resouce = ["project01_login:1", "project01_getPolicyInfo:1", "project01_clientList:1"]
    web_flow_model(data_resouce, "PyCharm", "di1")
