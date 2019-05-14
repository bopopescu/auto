# -*- coding:utf-8 -*-

from business.script.JsonParseDemo import JsonParse


def json_model_pub(data_source, version="st1", model="ride"):
    # 支持用Comment注释
    if data_source[0].lower() == "comment":
        return
    jsonparseclaas = JsonParse(data_source, version)
    jsonparseclaas.jsonparse_pub(model)


if __name__ == '__main__':

    # project02_demo
    data_source = [
                   "project02:login;index/;citycode/cmpPriv;fhCompanies",
                   "name:=admin;password:=admin123456",                     # 自定义替换接口参数
                   u"msg:=请求成功",
                   "level:=0",
                   u"msg:=请求成功",
                   "",
                   u"msg:=请求成功",
                   "",
                   u"msg:=请求成功;code:=200",
                ]

    # project01_demo
    # data_source = [
    #                "project01;project01.majorIssue:login;getGrid",
    #                "name:=zhangm002;password:=cmrh1875",
    #                u"msg:=请求成功",
    #                "pageNum:=2",                                              # 自定义替换接口参数
    #                u"msg:=请求成功",
    #             ]

    json_model_pub(data_source, "di1", "python")


