# -*- coding: utf-8 -*-

# @Time    : 2018/10/3 0003 2:23
# @Author  : Administrator
# @Comment : 


# --n的阶层
# 递归
def fact(n):
    if n == 1:
        return 1
    return n*fact(n-1)


# 尾递归
def fact_iter(num, product=1):
    if num == 1:
        return product
    return fact_iter(num-1, num*product)


# 循环
def fact_cycle(n):
    if n == 1:
        return 1
    else:
        tmp = 1
        for i in range(1, n+1):
            tmp = tmp*i
        return tmp


# --斐波那契数列
# 递归
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)


# 尾递归
def fib_iter(num, res=0, tmp=1):
    if num == 0:
        return res
    return fib_iter(num-1, tmp, res+tmp)


# 循环    斐波那契数列：0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...
def fib_cycle(n):
    if n < 2:
        return n
    else:
        c = 0
        a = 0
        b = 1
        for i in range(1, n):              # 注意是从1开始
            c = a + b
            a = b
            b = c
        return c


# 循环 -方法2    斐波那契数列：0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, ...
def fib_cycle02(n):
    lis = list()
    if n < 2:
        lis.append(n)
    else:
        a, b = 0, 1
        while n > 0:
            lis.append(b)
            # b = a + b
            # a = b
            a, b = b, a+b
            n -= 1
    return lis[n-1]

print fib_cycle02(0)
print fib_cycle02(1)
print fib_cycle02(2)
print fib_cycle02(10)

