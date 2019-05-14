# -*- coding: utf-8 -*-

# @Time    : 2018/9/26 10:17
# @Author  : songq001
# @Comment : 

import yaml
import os

yaml_path = os.getcwd() + "\%s" % "yaml01.yaml"
f = open(yaml_path, "r")

cfg = f.read()
print type(cfg)     # 读出来是字符串
# print cfg

d = yaml.load(cfg)  # 用load方法转字典,列表
print d
print type(d)


