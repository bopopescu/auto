# -*- coding: utf-8 -*-

# @Time    : 2018/9/29 16:33
# @Author  : songq001
# @Comment : 动态加载 （反射） 演示

import os
import sys


def run(cases, n, a, b,):
    # path = os.path.join(os.getcwd(), "script")
    from Reflection_Demo import path
    path = os.path.join(path, "Reflection_Demo", "script")
    sys.path.append(path)
    class_dict = dict()

    # 获取所有文件和文件夹
    dirs = os.listdir(path)
    # print dirs

    # for l in dirs:
    #     if l.endswith("py") and l not in ["__init__.py"]:
    #         mod = __import__(l[:-3])
    #         # print dir(mod)
    #         for c in dir(mod):
    #             if c not in ['__builtins__', '__doc__', '__file__', '__name__', '__package__', 'c', 'class_dict', 'dirs', 'l', 'mod', 'obj_class', 'os', 'path']:
    #                 obj_class = getattr(mod, c)
    #                 class_dict[c] = obj_class
    #                 # print class_dict

    # 不做多余排除亦可，兼容性更好，但效率相对会低
    for l in dirs:
        mod = __import__(l[:-3])
        # print dir(mod)
        for c in dir(mod):
            obj_class = getattr(mod, c)
            class_dict[c] = obj_class
            # print class_dict

    for cla, obj in class_dict.items():
        obj_method = getattr(obj, cases, None)
        if obj_method:
            obj_method = getattr(obj(a, b), cases)
            result = obj_method(n)
            print result
            if not result:
                print "result is 0."
            print "%s() method success!" % obj_method.__name__

if __name__ == '__main__':
    case = ["add", "factorial"]
    for k in case:
        run(k, 5, 1, 100)

    print run.__name__


