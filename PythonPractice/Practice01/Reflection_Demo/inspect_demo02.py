# -*- coding: utf-8 -*-

# @Time    : 2018/10/2 0002 0:39
# @Author  : Administrator
# @Comment : 

import sys  # 模块，sys指向这个模块对象
import inspect
import fnmatch as m


def foo(): pass  # 函数，foo指向这个函数对象


class Cat(object):  # 类，Cat指向这个类对象
    def __init__(self, name='kitty'):
        self.name = name

    def sayHi(self):  # 实例方法，sayHi指向这个方法对象，使用类或实例.sayHi访问
        print self.name, 'says Hi! '  # 访问名为name的字段，使用实例.name访问

cat = Cat()  # cat是Cat类的实例对象

print Cat.sayHi  # 使用类名访问实例方法时，方法是未绑定的(unbound)
print cat.sayHi  # 使用实例访问实例方法时，方法是绑定的(bound)

cat = Cat('kitty')
print cat.name  # 访问实例属性
cat.sayHi()  # 调用实例方法

print dir(cat)   # 获取实例的属性名，以列表形式返回
if hasattr(cat,  'name'):  # 检查实例是否有这个属性
    setattr(cat, 'name', 'tiger')  # same as: a.name = 'tiger'

print getattr(cat,  'name')  # same as: print a.name
getattr(cat, 'sayHi')()      # same as: cat.sayHi()


# 模块(module)
# __doc__: 文档字符串。如果模块没有文档，这个值是None。
# *__name__: 始终是定义时的模块名；即使你使用import .. as 为它取了别名，或是赋值给了另一个变量名。
# *__dict__: 包含了模块里可用的属性名-属性的字典；也就是可以使用模块名.属性名访问的对象。
# __file__: 包含了该模块的文件路径。需要注意的是内建的模块没有这个属性，访问它会抛出异常！
print "\n" + "#"*20 + "模块(module)" + "#"*20
print m. __doc__ .splitlines()[0]  # Filename matching with shell patterns.
print m. __name__   # fnmatch
print m. __file__   # C:\Python27\lib\fnmatch.pyc
print m. __dict__ .items()[0]    # ('fnmatchcase', )

# 类(class)
# __doc__: 文档字符串。如果类没有文档，这个值是None。
# *__name__: 始终是定义时的类名。
# *__dict__: 包含了类里可用的属性名-属性的字典；也就是可以使用类名.属性名访问的对象。
# __module__: 包含该类的定义的模块名；需要注意，是字符串形式的模块名而不是模块对象。
# *__bases__: 直接父类对象的元组；但不包含继承树更上层的其他类，比如父类的父类。
print "\n" + "#"*20 + "类(class)" + "#"*20
print Cat.__doc__       # None
print Cat. __name__     # Cat
print Cat. __module__   # __main__
print Cat. __bases__    # (,)
print Cat. __dict__     # {'__module__': '__main__', ...}


# 实例(instance)
# 实例是指类实例化以后的对象。
# *__dict__: 包含了可用的属性名-属性字典。
# *__class__: 该实例的类对象。对于类Cat，cat.__class__ == Cat 为 True。
print "\n" + "#"*20 + "实例(instance)" + "#"*20
print cat.__dict__
print cat. __class__
print cat. __class__ == Cat  # True
# print cat. __class__("111").sayHi()


# 方法(method)
# 方法虽然不是函数，但可以理解为在函数外面加了一层外壳；拿到方法里实际的函数以后，就可以使用2.5节的属性了。
# __doc__: 与函数相同。
# __name__: 与函数相同。
# *__module__: 与函数相同。
# im_func: 使用这个属性可以拿到方法里实际的函数对象的引用。另外如果是2.6以上的版本，还可以使用属性名__func__。
# im_self: 如果是绑定的(bound)，则指向调用该方法的类（如果是类方法）或实例（如果是实例方法），否则为None。如果是2.6以上的版本，还可以使用属性名__self__。
# im_class: 实际调用该方法的类，或实际调用该方法的实例的类。注意不是方法的定义所在的类，如果有继承关系的话。
print "\n" + "#"*20 + "方法(method)" + "#"*20
im = cat.sayHi
print im.__doc__
print im.__name__
print im.im_func
print im.__func__
print im.im_self   # cat
print im.__self__
print im.im_class  # Cat


# 生成器(generator)
# 生成器是调用一个生成器函数(generator function)返回的对象，多用于集合对象的迭代。
# __iter__: 仅仅是一个可迭代的标记。
# gi_code: 生成器对应的code对象。
# gi_frame: 生成器对应的frame对象。
# gi_running: 生成器函数是否在执行。生成器函数在yield以后、执行yield的下一行代码前处于frozen状态，此时这个属性的值为0。
# next|close|send|throw: 这是几个可调用的方法，并不包含元数据信息，如何使用可以查看生成器的相关文档。
def gen():
    for n in xrange(5):
        yield n
g = gen()
print "\n" + "#"*20 + "生成器(generator)" + "#"*20
print g             # <generator object gen at 0x...>
print g.gi_code     # <code object gen at 0x...>
print g.gi_frame    # <frame object at 0x...>
print g.gi_running  # 0
print g.next()      # 0
print g.next()      # 1
for n in g:
    print n,        # 2 3 4


# 代码块(code)
# 代码块可以由类源代码、函数源代码或是一个简单的语句代码编译得到。这里我们只考虑它指代一个函数时的情况；2.5节中我们曾提到可以使用函数的func_code属性获取到它。code的属性全部是只读的。
# co_argcount: 普通参数的总数，不包括*参数和**参数。
# co_names: 所有的参数名（包括*参数和**参数）和局部变量名的元组。
# co_varnames: 所有的局部变量名的元组。
# co_filename: 源代码所在的文件名。
# co_flags: 这是一个数值，每一个二进制位都包含了特定信息。较关注的是0b100(0x4)和0b1000(0x8)，如果co_flags & 0b100 != 0，说明使用了*args参数；如果co_flags & 0b1000 != 0，说明使用了**kwargs参数。另外，如果co_flags & 0b100000(0x20) != 0，则说明这是一个生成器函数(generator function)。
class Cat(object):  # 类，Cat指向这个类对象
    def __init__(self, name=' kitty '):
        self.name = name

    def sayHi(self):                    # 实例方法，sayHi指向这个方法对象，使用类或实例.sayHi访问
        print self.name, ' says Hi! '   # 访问名为name的字段，使用实例.name访问

cat = Cat('kitty')
co = cat.sayHi.__func__.func_code
# co = cat.__class__.sayHi.__func__.func_code   # 效果同上
# co = Cat.sayHi.__func__.func_code             # 效果同上
# co = cat.sayHi.func_code                      # 效果同上
print "\n"
print "#"*20 + "代码块(code)" + "#"*20
print co
print co.co_argcount    # 1
print co.co_names       # ('name',)
print co.co_name        # sayHi
print co.co_varnames    # ('self',)
print co.co_flags & 0b100  # 0


# 栈帧(frame)
# 栈帧表示程序运行时函数调用栈中的某一帧。函数没有属性可以获取它，因为它在函数调用时才会产生，而生成器则是由函数调用返回的，所以有属性指向栈帧。想要获得某个函数相关的栈帧，则必须在调用这个函数且这个函数尚未返回时获取。你可以使用sys模块的_getframe()函数、或inspect模块的currentframe()函数获取当前栈帧。这里列出来的属性全部是只读的。
# f_back: 调用栈的前一帧。
# f_code: 栈帧对应的code对象。
# f_locals: 用在当前栈帧时与内建函数locals()相同，但你可以先获取其他帧然后使用这个属性获取那个帧的locals()。
# f_globals: 用在当前栈帧时与内建函数globals()相同，但你可以先获取其他帧……。
def add(x, y=1):
    f = inspect.currentframe()
    print f.f_locals    # same as locals()
    print f.f_back      # <frame object at 0x...>
    print f.f_code      # <code object add at 00000000024C19B0, file "E:/work_2/git_songq/PythonPractice/test01/Reflection_Demo/inspect_demo02.py", line 147>
    print f.f_code.co_name
    return x + y
print "\n" + "#"*20 + "栈帧(frame)" + "#"*20
add(2)


# 追踪(traceback)
# 追踪是在出现异常时用于回溯的对象，与栈帧相反。由于异常时才会构建，而异常未捕获时会一直向外层栈帧抛出，所以需要使用try才能见到这个对象。你可以使用sys模块的exc_info()函数获得它，这个函数返回一个元组，元素分别是异常类型、异常对象、追踪。traceback的属性全部是只读的。
# tb_next: 追踪的下一个追踪对象。
# tb_frame: 当前追踪对应的栈帧。
# tb_lineno: 当前追踪的行号。
def div(x, y):
    try:
        return x/y
    except ZeroDivisionError as e:
    # except:
        tb = sys.exc_info()  # return (exc_type, exc_value, traceback)
        print tb
        print tb[2].tb_lineno      # "return x/y"的行号
        print e.message
        # raise ZeroDivisionError("Error message: " + e.message)
print "\n" + "#"*20 + "追踪(traceback)" + "#"*20
div(1, 0)


class Foo(object):
    """Foo doc"""
    def __init__(self, name):
        self.__name = name

    def getname(self):
        return self.__name

ins = inspect.getmembers(Foo, inspect.ismethod)
# sources = inspect.getsource(inspect)
sources = inspect.getsource(Foo)
module = inspect.getmodule(Foo)
print "\n" + "#"*20 + "inspect" + "#"*20
print inspect.ismethod(Foo.getname)
print inspect.ismethod(Foo)
print inspect.isclass(Foo)
print ins
print sources
print module
for i in ins:
    if "getname" in i[0]:
        print i[1]



