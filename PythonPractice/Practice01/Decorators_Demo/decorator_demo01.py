# -*- coding: utf-8 -*-

# @Time    : 2018/10/8 17:12
# @Author  : songq001
# @Comment : 装饰器

"""
装饰器-示例
资料参考学习：http://python.jobbole.com/81683/
https://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001386819866394c3f9efcd1a454b2a8c57933e976445c0000

所谓装饰器就是把函数包装一下，为函数添加一些(公共的）附加功能，装饰器就是一个函数，参数为被包装的函数，返回包装后的函数
5个理由告诉你为什么要学习使用Python装饰器：http://python.jobbole.com/85393/
"""


# 嵌套函数
# Python允许创建嵌套函数。这意味着我们可以在函数里面定义函数而且现有的作用域和变量生存周期依旧适用。
def outer():
     x = 1
     def inner():
         print x    # 1
     inner()        # 2

outer()


# 函数是python世界里的一级类对象
# 显而易见，在python里函数和其他东西一样都是对象。包含变量的函数，你也并不是那么特殊！
print issubclass(int, object)     # all objects in Python inherit from a common baseclass
def foo():
     pass

print foo.__class__
print issubclass(foo.__class__, object)


def add(x, y):
     return x + y
def sub(x, y):
     return x - y
def apply(func, x, y):  # 1
     return func(x, y)  # 2

print apply(add, 2, 1)    # 3
print apply(sub, 2, 1)


def outer():
    def inner():
        print "Inside inner"
    return inner    # 1
foo = outer()       # 2
print foo           # doctest:+ELLIPSIS
print foo()


# ========================================
# 闭包
# ========================================
def outer():
    x = 1
    def inner():
        print x     # 1
    return inner

foo = outer()
print foo.func_closure  # doctest: +ELLIPSIS
# print foo()


# =====稍微改动
def outer(x):
    def inner():
        print x  # 1
    return inner
print1 = outer(1)
print2 = outer(2)
print print1()
print print2()


# ========================================
# 装饰器 : 装饰器其实就是一个闭包，把一个函数当做参数然后返回一个替代版函数。我们一步步从简
# ========================================
def outer(some_func):
    def inner():
        print "before some_func"
        ret = some_func()  # 1
        return ret + 1
    return inner


def foo():
    return 1
print "=================装饰器======================="
decorated = outer(foo)  # 2
print decorated()


# example
class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Coord: " + str(self.__dict__)


def add(a, b):
    return Coordinate(a.x + b.x, a.y + b.y)


def sub(a, b):
    return Coordinate(a.x - b.x, a.y - b.y)

one = Coordinate(100, 200)
two = Coordinate(300, 200)
three = Coordinate(-100, -100)
print add(one, two)
print sub(one, two)


def wrapper(func):
    """
    我们期望在不更改坐标对象one, two, three的前提下one减去two的值是{x: 0, y: 0}，one加上three的值是{x: 100, y: 200}。
    与其给每个方法都加上参数和返回值边界检查的逻辑，我们来写一个边界检查的装饰器
    """
    def checker(a, b):  # 1
        if a.x < 0 or a.y < 0:
            a = Coordinate(a.x if a.x > 0 else 0, a.y if a.y > 0 else 0)
        if b.x < 0 or b.y < 0:
            b = Coordinate(b.x if b.x > 0 else 0, b.y if b.y > 0 else 0)
        ret = func(a, b)
        if ret.x < 0 or ret.y < 0:
            ret = Coordinate(ret.x if ret.x > 0 else 0, ret.y if ret.y > 0 else 0)
        return ret

    return checker

add = wrapper(add)
sub = wrapper(sub)
print sub(one, two)
print add(one, three)


# *args and **kwargs
def one(*args):
    print args          # 1

print "=================*args and **kwargs======================="
one()
one(1, 2, 3)


def two(x, y, *args):   # 2
    print x, y, args
two('a', 'b', 'c')


def add(x, y):
    return x + y

lst = [1, 2]
print add(lst[0], lst[1])       # 1
print add(*lst)                 # 2


def foo(**kwargs):
    print kwargs

foo()
foo(x=1, y=2)


dct = {'x': 1, 'y': 2}
def bar(x, y):
     return x + y
print bar(**dct)


"""
更通用的装饰器
"""
def logger(func):
    def inner(*args, **kwargs):  # 1
        print "Arguments were: %s, %s" % (args, kwargs)
        return func(*args, **kwargs)  # 2

    return inner


@logger
def foo1(x, y=1):
    return x * y


@logger
def foo2():
    return 2

print "=================更通用的装饰器======================="
print foo1(5, 4)
print foo1(1)
print foo2()


"""
传入参数: 需要编写一个返回decorator的高阶函数,更复杂
"""
def log(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print '%s %s():' % (text, func.__name__)
            return func(*args, **kw)
        return wrapper
    return decorator

@log('execute')
def now():
    print '2013-12-25'

print "=================传入参数的装饰器======================="
now()
now1 = log('execute')(now)
now1()


import functools
def log01(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print 'call %s():' % func.__name__
        return func(*args, **kw)
    return wrapper


@log01
def f():
    pass


def log02(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print '%s %s():' % (text, func.__name__)
            return func(*args, **kw)
        return wrapper
    return decorator


@log02('execute')
def f():
    pass

f1 = log02('execute')(f)
f1()


