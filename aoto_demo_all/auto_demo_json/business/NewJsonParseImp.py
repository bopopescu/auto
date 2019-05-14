# -*- coding:utf-8 -*-

from business.script.NewJsonParseDemo import NewJsonParse


def json_model_pub(data_source, version="st1", model="ride"):
    # 支持用Comment注释
    if data_source[0].lower() == "comment":
        return
    jsonparseclaas = NewJsonParse(data_source, version)
    jsonparseclaas.new_jsonparse_pub(model)


if __name__ == '__main__':

    # project02_demo
    # data_source = [
    #                "project02:login",
    #                "name:=admin;password:=admin123456",                     # 自定义替换接口参数
    #                u"msg:=请求成功",
    #                "project02:index/",
    #                "level:=0",
    #                u"msg:=请求成功",
    #                "project02:citycode/cmpPriv",
    #                "",
    #                u"msg:=请求成功",
    #                "project02:fhCompanies",
    #                "",
    #                u"msg:=请求成功;code:=200",
    #             ]

    # project01_demo
    data_source = [
                   "project01:login",
                   "name:=zhangm002;password:=cmrh1875",
                   u"msg:=请求成功",
                   "project01.majorIssue:getGrid",
                   "pageNum:=2",                                              # 自定义替换接口参数
                   u"msg:=请求成功",
                ]

    json_model_pub(data_source, "di1", "python")


