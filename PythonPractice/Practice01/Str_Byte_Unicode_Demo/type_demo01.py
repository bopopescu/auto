# -*- coding: utf-8 -*-

# @Time    : 2018/10/19 16:50
# @Author  : songq001
# @Comment : 




def my_t_02():
    """
    关于python2中的unicode和str以及python3中的str和bytes
    https://www.cnblogs.com/yangmingxianshen/p/7990102.html
    在Python2中，作为两种类型的字符序列，str与unicode需要转换，它们是这样转换的.
    str——decode方法——》unicode——encode方法——》str
    在python3中可以这样对应这转换，配合上面的图，也许会好理解一点。
    byte——decode（解码）方法——》str——>encode（编码）方法——》byte
    :return: 
    """
    my_bytes = 'byte类型'
    print type(my_bytes)
    # str to bytes
    # my_bytes_02 = my_bytes.encode('utf-8')      # 通过encode()把str转成byte  注：python3中的方法， python2报错
    # my_bytes_02 = bytes(my_bytes, encoding='utf8')  # 效果同上    注：python3中的方法， python2报错
    # print type(my_bytes_02)

    # bytes to str
    # my_bytes_03 = my_bytes_02.decode('utf-8')
    # my_bytes_03 = str(my_bytes_02, encoding="utf-8")

    my_bytes_00 = unicode(my_bytes, encoding='utf-8')
    my_bytes_001 = my_bytes.decode('utf-8')             # 效果同上
    print type(my_bytes_00)
    print type(my_bytes_001)
    print type(u'byte类型')
    my_bytes_002 = my_bytes_001.encode('utf-8')
    # my_bytes_003 = unicode.encode(my_bytes_001)
    print type(my_bytes_002)


if __name__ == '__main__':
        pass
        my_t_02()

