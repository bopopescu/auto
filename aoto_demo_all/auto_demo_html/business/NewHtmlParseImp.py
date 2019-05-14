# -*- coding:utf-8 -*-

from business.script.NewHtmlParseDemo import NewHtmlParse
import threading


def html_model_pub(data_source, version="1221", model="ride"):
    # 支持用Comment注释
    if data_source[0].lower() == "comment":
        return
    htmlparseclaas = NewHtmlParse(data_source, version)
    htmlparseclaas.new_htmlparse_pub(model)


if __name__ == '__main__':

    tasks = [

        # demo1
        [
            "project01:getVerifyCode.do",
            "",
            u"ResultMsgContain:=JFIF",
            "project01:Login.sso",
            "",
            u"ResultMsgContain:=会话"
        ],
        # demo2
        [
            "project01:login",
            "username:=L000000001@cmrhagent.com;password:=cmrh1875",
            u"msg:=登陆成功",
            "project01:uploadImage",
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


