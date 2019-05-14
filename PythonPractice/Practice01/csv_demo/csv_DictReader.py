# -*- coding: utf-8 -*-

# @Time    : 2018/9/30 17:28
# @Author  : songq001
# @Comment : 

import csv


with open('name.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    print type(reader)
    for row in reader:
        # 循环打印数据的id和class值，此循环执行7次
        print row

with open('name.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for i in enumerate(reader):
        print i

items = {'id': '0', 'class': '5'}
print items.items()             # [('id', '0'), ('class', '5')]
