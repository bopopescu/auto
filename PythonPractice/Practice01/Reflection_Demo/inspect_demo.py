# -*- coding: utf-8 -*-

# @Time    : 2018/9/30 17:21
# @Author  : songq001
# @Comment : https://blog.csdn.net/yugongpeng_blog/article/details/45670805

import sys
import inspect


class Inspect_Demo(object):

    # 获取类名方法
    def get_classname(self):
        return self.__class__.__name__

    # 获取类名方法1   返回 方法名.properties
    def get_current_function_name(self):
        return "%s.%s" % (inspect.stack()[1][3], "properties")

    # 获取类名方法   返回 方法名.txt
    def get_current_function_name_txt(self):
        return "%s.%s" % (inspect.stack()[1][3], "txt")

    # 获取类名方法2
    def get_methodname(self):
        return sys._getframe().f_code.co_name
        # return inspect.currentframe().f_code.co_name   # 效果同上

    # 获取 [类名.方法名] 方法
    def get_wholename(self):
        return "%s.%s" % (self.__class__.__name__, self.get_current_function_name())


if __name__ == '__main__':
    o = Inspect_Demo()
    print o.get_classname()
    print o.get_current_function_name()
    print o.get_current_function_name_txt()
    print o.get_methodname()
    print o.get_wholename()

