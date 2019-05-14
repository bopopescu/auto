# -*- coding: utf-8 -*-

# @Time    : 2018/5/16 18:46
# @Author  : songq001
# @Comment : 


from django.http import HttpResponse
from django.shortcuts import render

# def hello(request):
#     return HttpResponse("Hello world ! ")


def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)

