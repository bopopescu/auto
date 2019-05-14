# -*- coding: utf-8 -*-

# @Time    : 2018/7/18 10:22
# @Author  : songq001
# @Comment : 

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!================'

if __name__ == '__main__':
    app.run()

