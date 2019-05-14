#!/usr/bin/env python
# coding=utf-8

# ****************************************************************
# app_com.py  
# Author     : Lieb  
# Version    : 1.1 
# Date       : 2015-6-24 
# Description: app公共库  
# ****************************************************************
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.mobileby import MobileBy as By
from titanrun.common.Result import Result
from titanrun.config import Settings
import time
import os


class Action(object):
    def __init__(self, driver):
        self.driver = driver

    def open(self, url):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()

    def find_toast(self, message, timeout=Settings.EXTREME_TIMEOUT):
        """判断toast信息,需要设置desired_caps['automationName'] = 'uiautomator2'"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@text=\'{}\']'.format(message))))
            return True
        except Exception as e:
            print(e)
            return False

    def getsize(self):
        # 得到屏幕分辨率
        size = self.driver.get_window_size()
        x = size.get('width')
        y = size.get('height')
        return (x, y)

    def swipeleft(self, t=None):
        # 左滑
        l = self.getsize()
        x1 = int(l[0] * 0.95)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.1)
        self.driver.swipe(x1, y1, x2, y1, t)

    def swiperight(self, t=None):
        # 右滑
        l = self.getsize()
        x1 = int(l[0] * 0.95)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.1)
        self.driver.swipe(x2, y1, x1, y1, t)

    def swipedown(self, t=None):
        # 下滑
        l = self.getsize()
        x1 = int(l[0] * 0.5)
        y1 = int(l[1] * 0.2)
        y2 = int(l[1] * 0.8)
        self.driver.swipe(x1, y1, x1, y2, t)

    def swipeup(self, t=None):
        # 上滑
        l = self.getsize()
        x1 = int(l[0] * 0.5)
        y1 = int(l[1] * 0.3)
        y2 = int(l[1] * 0.7)
        self.driver.swipe(x1, y2, x1, y1, t)

    def isElementExist(self, value, by=By.IOS_PREDICATE, timeout=Settings.LARGE_TIMEOUT):
        # 判断元素是否存在
        try:
            self.findElement(value, by, timeout)
            return True
        except Exception as e:
            return False

    def isTextExist(self, text, timeout=Settings.LARGE_TIMEOUT):
        # Android 上，主要使用元素的content-desc属性
        # 在 iOS 上，主要使用元素的label或name属性
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.find_element(*(By.ACCESSIBILITY_ID, text)).is_displayed())
            return True
        except Exception as e:
            print("not find text %s" % text)
            self.save_pic('err')
            return False

    def find_element(self, element, timeout=Settings.EXTREME_TIMEOUT):
        # 找元素,element格式(by, value)
        try:
            ele = WebDriverWait(self.driver, timeout).until(lambda driver: driver.find_element(*element))
            return ele
        except Exception as e:
            self.save_pic('err')
            raise Exception('not find %s' % element)

    def find_elements(self, element, timeout=Settings.EXTREME_TIMEOUT):
        # 找元素列表,element格式(by, value)
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.find_element(*element).is_displayed())
            return self.driver.find_elements(*element)
        except Exception as e:
            self.save_pic('err')
            raise Exception('not find %s'%element)

    def findElement(self, value, by=By.IOS_PREDICATE, timeout=Settings.EXTREME_TIMEOUT):
        if value.startswith('com'):
            by = By.ID
        elif value.startswith('//'):
            by = By.XPATH
        elif value.startswith('android') or value.startswith('XCUIElement'):
            by = By.CLASS_NAME
        elif value.startswith('new'):
            by = By.ANDROID_UIAUTOMATOR
        element = (by, value)
        return self.find_element(element, timeout)

    def findElements(self, value, by=By.IOS_PREDICATE, timeout=Settings.EXTREME_TIMEOUT):
        if value.startswith('com'):
            by = By.ID
        elif value.startswith('//'):
            by = By.XPATH
        elif value.startswith('android') or value.startswith('XCUIElement'):
            by = By.CLASS_NAME
        elif value.startswith('new'):
            by = By.ANDROID_UIAUTOMATOR
        element = (by, value)
        return self.find_elements(element, timeout)

    def click_android_text(self, text, timeout=Settings.EXTREME_TIMEOUT):
        try:
            ele = WebDriverWait(self.driver, timeout).until(lambda driver: driver.find_element(*(By.ANDROID_UIAUTOMATOR, 'new UiSelector().text("%s")'%text)))
            ele.click()
        except Exception as e:
            self.save_pic('err')
            raise Exception('not find text %s'%text)

    def click_ios_text(self, text, timeout=Settings.EXTREME_TIMEOUT):
        # 在 iOS 上，主要使用元素的label或name属性
        try:
            ele = WebDriverWait(self.driver, timeout).until(lambda driver: driver.find_element(*(By.ACCESSIBILITY_ID, text)))
            ele.click()
        except Exception as e:
            self.save_pic()
            raise Exception('not find text %s'%text)

    def click(self, value, by=By.IOS_PREDICATE):
        ele = self.findElement(value, by)
        ele.click()

    def update_text(self, value, text, by=By.IOS_PREDICATE):
        ele = self.findElement(value, by)
        self.driver.set_value(ele, text)

    def get_text(self, value, by=By.IOS_PREDICATE):
        ele = self.findElement(value, by)
        return ele.text

    def switch_to_context(self, context):
        self.driver.switch_to.context(context)

    def assert_data(self, expect, actual=None):
        result = Result()
        try:
            if expect and actual:
                assert expect == actual
            else:
                assert expect
            self.save_pic('ok')
            print('%s*****用例断言成功!'%self)
            result.flag = True
        except Exception as e:
            image = self.save_pic('err')
            if actual:
                msg = '%s*****用例断言失败: %s != %s' % (self, expect, actual)
            else:
                msg = '%s*****用例断言失败: %s' % (self, expect)
            print(msg)
            result.flag = False
            result.msg = msg
            result.image = image
        return result

    def save_pic(self, name='pic'):
        """保存截图方法"""
        try:
            now_day = time.strftime("%Y%m%d", time.localtime(time.time()))
            now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            path = '.' + os.path.sep + 'images' + os.path.sep + now_day + os.path.sep
            if not os.path.exists(path):
                os.makedirs(path)
            image = path + r'%s-%s.png' % (name, now)
            self.driver.get_screenshot_as_file(image)
            print('截图保存路径为:%s' % os.path.abspath(image))
        except Exception as e:
            print('保存截图失败:%s'%e)
        return image
