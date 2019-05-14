# coding: utf-8

"""
函数式编程：
     python特点：不是纯函数式编程（允许变量存在）；
                              支持高阶函数（可以传入函数作为变量）；
                              支持闭包（可以返回函数）；
                              有限度的支持匿名函数；
     高阶函数：变量可以指向函数；
                           函数的参数可以接收变量；
                           一个函数可以接收另一个函数作为参数；
"""

import math
import time
import functools


def add(x, y, f):
    return f(x) + f(y)


print add(10, 11, abs)


def format_name(s):
    return s.title()

print map(format_name, ['adam', 'LISA', 'barT'])


def prod(x, y):
    return x+y

print reduce(prod, (1, 2, 3, 18))


def is_sqr(x):
    return int(math.sqrt(x))*int(math.sqrt(x)) == x

print filter(is_sqr, range(1, 101))


def cmp_ignore_case(s1, s2):
    return cmp(s1.lower(), s2.lower())

print sorted(['bob', 'about', 'Zoo', 'Credit'], cmp_ignore_case)


# 返回函数
def calc_prod(lst):
    def prod01(x, y):
        return x * y

    def g():
        return reduce(prod01, lst)

    return g

f = calc_prod([1, 2, 3, 4])
print f()


# 闭包：内层函数使用外层函数的参数，然后返回内层函数；
def count():
    fs = []
    for i in range(1, 4):
        def f(j):
            def g():
              return j*j
            return g
        # 调用内层函数
        fs.append(f(i))
    return fs

f1, f2, f3 = count()
print f1(), f2(), f3()


# 装饰器：给函数添加新功能，并简化该函数调用；
def log(f):
    def fn(*args, **kw):  # *args，**kw保证对任意个数参数都能正常调用
        print 'call ' + f.__name__ + '()...'
        return f(*args, **kw)

    return fn


@log  # 调用日志装饰器
def factorial(n):
    return reduce(lambda x, y: x * y, range(1, n + 1))

print factorial(10)


# 带参数的装饰器
def log(prefix):
    def log_decorator(f):
        def wrapper(*args, **kw):
            print '[%s] %s()...' % (prefix, f.__name__)
            return f(*args, **kw)

        return wrapper

    return log_decorator


@log('DEBUG')  # DEBUG为给装饰器传入的参数
def decorators_test():
    pass

decorators_test()


def performance(unit):
    def perf_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kw):
            t1 = time.time()
            r = f(*args, **kw)
            t2 = time.time()
            t = (t2 - t1) * 1000 if unit == 'ms' else (t2 - t1)
            print 'call %s() in %f %s' % (f.__name__, t, unit)
            return r

        return wrapper

    return perf_decorator


@performance('ms')
def factorial(n):
    return reduce(lambda x, y: x * y, range(1, n + 1))

print factorial(10)

# 二进制转十进制
int2 = functools.partial(int, base=2)
print int2('1011')

