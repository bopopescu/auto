# -*- coding: utf-8 -*-

# @Time    : 2018/10/2 0002 1:53
# @Author  : Administrator
# @Comment : 


# 简单生成器 : 要创建一个generator，有很多种方法。第一种方法很简单，只要把一个列表生成式的[]改成()，就创建了一个generator
L = [x * x for x in range(10)]
print L
g = (x * x for x in range(10))
print g
for i in g:         # 打印方法1
    print i
# print '#'*20
# print g.next()    # 打印方法2
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()
# print g.next()      # 没有更多的元素时，抛出StopIteration的错误


# 带yield 语句的生成器
# generator和函数的执行流程不一样。函数是顺序执行，遇到return语句或者最后一行函数语句就返回。而变成generator的函数，在每次调用next()的时候执行，遇到yield语句返回，再次执行时从上次返回的yield语句处继续执行。
def odd():
    print "step 1"
    yield 1
    print "step 2"
    yield 3
    print "step 3"
    yield 5
print "\n" + "#"*20 + "odd()" + "#"*20
o = odd()
print o.next()
o = odd()
print o.next()
o = odd()
print o.next()


def fib(max):
    """
    把fib函数变成generator  (函数和generator仅一步之遥。要把fib函数变成generator，只需要把print b改为yield b就可以了)
    :param max:
    :return:
    """
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n = n + 1

f = fib(6)
print "\n" + "#"*20 + "fib()" + "#"*20
print f
for fi in f:
    print fi


# 加强的生成器
# 在 python2.5中,一些加强特性加入到生成器中,所以除了next()来获得下个生成的值,用户可以将值回送给生成器[send()],在生成器中抛出异常,以及要求生成器退出[close()]
def gen(x):
    count = x
    while True:
        val = (yield count)
        if val is not None:
            count = val
        else:
            count += 1

f = gen(5)
print "\n" + "#"*20 + "gen()" + "#"*20
print f.next()
print f.next()
print f.next()
print '===================='
print f.send(10)     # 发送数字10给生成器 并返回10
print f.next()       # next()则从11开始
print f.next()
f.close()           # 退出生成器，后面的f.next()不在输出
print f.next()
print f.next()

