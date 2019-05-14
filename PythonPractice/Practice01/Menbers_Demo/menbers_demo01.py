# -*- coding: utf-8 -*-

# @Time    : 2018/10/8 15:05
# @Author  : songq001
# @Comment : 

"""
成员: 分别有静态字段、静态方法、类方法、特性、普通字段、普通方法

静态字段：存在类中 ,静态字段存在的意：把对象里面重复的数据只在类里保存一份
静态方法 ：没有self 可以传参数,调用的时候也需要传入参数 ,存在的意义:不需要创建对象，就可以访问此方法 ,为类而生
类方法:必须要有个cls参数：自动传入类名
特性  对象调用 、不能加参数，执行不用加括号
普通字段,存放在对象中
普通方法  存在的意义:普通方法如果要想被调用就需要创建self ,为对象而生
各成员存在的意义


成员小节：
自己去访问自己的成员，除了类中的方法
通过类访问的有:静态字段、静态方法、类方法
通过对象访问：普通字段、普通方法 、特性
"""


class Provice:
    # 静态字段
    country = 'China'

    def __init__(self, name):
        # 普通字段
        self.name = name
        # 普通方法

    def show(self):
        print('show')

    @staticmethod  # 静态方法
    def xo(arg):
        print('xo')
        print(arg)

    @classmethod  # 类方法，必须要有个cls参数：自动传入类名
    def xxoo(cls):
        print('xxoo', cls)

    def start(self):
        print('start')

    @property  # 特性
    def end(self):
        print('end')

    @end.setter
    def end(self, values):
        print(values)
        self.name = values  # 也可以更改内存里的值


Provice.country  # 类访问静态字段
Provice.xo('alex')  # 类访问静态方法
Provice.xxoo()  # 访问类方法

# 获取特性值
obj = Provice('alex')
obj.end
# 设置特性值
obj1 = Provice('alex')
obj1.end = '123'
print(obj1.name)

# 普通方法
obj1 = Provice('alex')
obj1.show()

# 普通字段
obj1 = Provice('alex')
print(obj1.name)


"""
成员修饰符:
公有成员：任何地方都能访问
私有成员：只有在类的内部才能访问，定义方式为命名时，前两个字符为下划线，如 "__test"
小节：私有成员只能在类内部使用，其他的都不能使用包括继承的子类，也不是绝对 也可以通过访问，但是不推荐
对象._类名__字段名
"""
class Person:
    country = 'China'   # 静态字段，属于公有成员
    __planet = 'Earth'  # 静态字段，属于私有成员

    def __init__(self, name):
        print('Person build self.name')
        self.name = name

    def say(self):
        print('The planet is %s' % Person.__planet)  # 在类的内部访问私有静态字段


p1 = Person('Nothing')
p1.say()
print(p1.country)   # 访问公有静态字段
# print(p1.__planet)  # 访问私有静态字段     抛异常：AttributeError: Person instance has no attribute '__planet'


"""
=============单例模式=============
单例模式，也叫单子模式，是一种常用的软件设计模式。在应用这个模式时，单例对象的类必须保证只有一个实例存在。许多时候整个系统只需要拥有一个的全局对象，这样有利于我们协调系统整体的行为。
"""
print "=============单例模式============="
# 用装饰器方式实现
def wapper(cls):
    instances = {}
    def inner():
        if cls not in instances:
            instances[cls] = cls()
        return cls
    return inner


@wapper
def Foo():
    pass

f1 = Foo()
f2 = Foo()
print(f1 is f2)


# 静态方法实现
class ConnectPool:
    __instatnce = None

    @staticmethod
    def get_instance():
        if ConnectPool.__instatnce:
            return ConnectPool.__instatnce
        else:
            ConnectPool.__instatnce = ConnectPool()
            return ConnectPool.__instatnce

obj = ConnectPool.get_instance()
print(obj)
obj1 = ConnectPool.get_instance()
print(obj1)

