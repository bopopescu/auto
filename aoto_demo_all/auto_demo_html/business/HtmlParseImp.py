# -*- coding:utf-8 -*-

from business.script.HtmlParseDemo import HtmlParse
import threading


def html_model_pub(data_source, version="1221", model="ride"):
    # 支持用Comment注释
    if data_source[0].lower() == "comment":
        return
    htmlparseclaas = HtmlParse(data_source, version)
    htmlparseclaas.htmlparse_pub(model)


if __name__ == '__main__':

    tasks = [

        # demo1
        [
            "project01:getVerifyCode.do;Login.sso",
            "",
            u"ResultMsgContain:=JFIF",
            "",
            u"ResultMsgContain:=会话"
        ],
        # demo2
        [
            "project01:login;uploadImage",
            "username:=L000000001@cmrhagent.com;password:=cmrh1875",
            u"msg:=登陆成功",
            "pimageType:=1337",
            u"flag:=Y;message:=成功"
        ],
    ]

    threads = []
    for task in tasks:
        threads.append(threading.Thread(html_model_pub(task, "di1", "python")))
    import time

    print time.strftime("%Y-%m-%d %H:%M:%S")
    for t in threads:
        t.start()
    print time.strftime("%Y-%m-%d %H:%M:%S")


