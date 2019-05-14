# -*- coding=UTF-8 -*-
import json
import logging
import math
import sys
import time
from bs4 import BeautifulSoup
# from titanrun.config import Settings
import titanrun.config.Settings as Settings
from titanrun.fixtures import Constants
from titanrun.fixtures import PageActions
from titanrun.fixtures import PageUtils
from titanrun.fixtures import XpathToCss
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException

class BaseCase(object):

    def __init__(self,driver,browser="chrome",version="st1"):
        self.driver = driver
        self.browser = browser
        self.timeout_multiplier = True
        self.demo_mode = None
        self.environment = None
        self.page_check_count = 0
        self.page_check_failures = []
        self._html_report_extra = []
        self.version = version

    def teardown(self):
        self.driver.quit()

    def open(self, url):
        try:
            self.driver.get(url)
        except Exception, e:
            time.sleep(Settings.TINY_TIMEOUT)
            self.driver.get(url)
        if Settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
            self.wait_for_ready_state_complete()

    def open_url(self, url):
        self.open(url)

    def click_text(self,val,by="*"):
        self.click("//%s[text()='%s']" %(by,val))

    def click(self, selector, by=By.CSS_SELECTOR,
              timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        element = PageActions.wait_for_element_visible(
            self.driver, selector, by, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            element.click()
        except:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = PageActions.wait_for_element_visible(
                self.driver, selector, by, timeout=timeout)
            element.click()
        if Settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()

    def double_click(self, selector, by=By.CSS_SELECTOR,
                     timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        element = PageActions.wait_for_element_visible(
            self.driver, selector, by, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.double_click(element)
            actions.perform()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = PageActions.wait_for_element_visible(
                self.driver, selector, by, timeout=timeout)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.double_click(element)
            actions.perform()
        if Settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()

    def click_chain(self, selectors_list, by=By.CSS_SELECTOR,
                    timeout=Settings.SMALL_TIMEOUT, spacing=0):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        for selector in selectors_list:
            self.click(selector, by=by, timeout=timeout)
            if spacing > 0:
                time.sleep(spacing)

    def click_link_text(self, link_text, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if self.browser == 'phantomjs':
            if self.is_link_text_visible(link_text):
                element = self.wait_for_link_text_visible(link_text)
                element.click()
                return
            source = self.driver.page_source
            soup = BeautifulSoup(source, "html.parser")
            html_links = soup.find_all('a')
            for html_link in html_links:
                if html_link.text == link_text:
                    if html_link.has_attr('href'):
                        href = html_link.get('href')
                        if href.startswith('//'):
                            link = "http:" + href
                        elif href.startswith('/'):
                            url = self.driver.current_url
                            domain_url = self.get_domain_url(url)
                            link = domain_url + href
                        else:
                            link = href
                        self.open(link)
                        return
                    raise Exception(
                        'Could not parse link from link_text [%s]' % link_text)
            raise Exception("Link text [%s] was not found!" % link_text)
        # Not using phantomjs
        element = self.wait_for_link_text_visible(link_text, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            element.click()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.wait_for_link_text_visible(
                link_text, timeout=timeout)
            element.click()
        if Settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()

    def click_partial_link_text(self, partial_link_text,
                                timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if self.browser == 'phantomjs':
            if self.is_partial_link_text_visible(partial_link_text):
                element = self.wait_for_partial_link_text(partial_link_text)
                element.click()
                return
            source = self.driver.page_source
            soup = BeautifulSoup(source)
            html_links = soup.fetch('a')
            for html_link in html_links:
                if partial_link_text in html_link.text:
                    for html_attribute in html_link.attrs:
                        if html_attribute[0] == 'href':
                            href = html_attribute[1]
                            if href.startswith('//'):
                                link = "http:" + href
                            elif href.startswith('/'):
                                url = self.driver.current_url
                                domain_url = self.get_domain_url(url)
                                link = domain_url + href
                            else:
                                link = href
                            self.open(link)
                            return
                    raise Exception(
                        'Could not parse link from partial link_text '
                        '[%s]' % partial_link_text)
            raise Exception(
                "Partial link text [%s] was not found!" % partial_link_text)
        # Not using phantomjs
        element = self.wait_for_partial_link_text(
            partial_link_text, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            element.click()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.wait_for_partial_link_text(
                partial_link_text, timeout=timeout)
            element.click()
        if Settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()

    def get_text(self, selector, by=By.CSS_SELECTOR,
                 timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        element = PageActions.wait_for_element_visible(
            self.driver, selector, by, timeout)
        try:
            element_text = element.text
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = PageActions.wait_for_element_visible(
                self.driver, selector, by, timeout)
            element_text = element.text
        return element_text

    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR,
                      timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        element = PageActions.wait_for_element_present(
            self.driver, selector, by, timeout)
        try:
            attribute_value = element.get_attribute(attribute)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = PageActions.wait_for_element_present(
                self.driver, selector, by, timeout)
            attribute_value = element.get_attribute(attribute)
        if attribute_value is not None:
            return attribute_value
        else:
            raise Exception("Element [%s] has no attribute [%s]!" % (
                selector, attribute))

    def refresh_page(self):
        self.driver.refresh()

    def get_current_url(self):
        return self.driver.current_url

    def get_page_source(self):
        return self.driver.page_source

    def get_page_title(self):
        return self.driver.title

    def go_back(self):
        self.driver.back()

    def go_forward(self):
        self.driver.forward()

    def close(self):
        self.driver.close()

    def get_image_url(self, selector, by=By.CSS_SELECTOR,
                      timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.get_attribute(selector,
                                  attribute='src', by=by, timeout=timeout)

    def add_text(self, selector, new_value, by=By.CSS_SELECTOR,
                 timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                if Settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
                    self.wait_for_ready_state_complete()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                if Settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
                    self.wait_for_ready_state_complete()

    def send_keys(self, selector, new_value, by=By.CSS_SELECTOR,
                  timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.add_text(selector, new_value, by=by, timeout=timeout)

    def update_text_value(self, selector, new_value, by=By.CSS_SELECTOR,
                          timeout=Settings.SMALL_TIMEOUT, retry=False):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        try:
            element.clear()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            element.clear()
        pre_action_url = self.driver.current_url
        try:
            if not new_value.endswith('\n'):
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                if Settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
                    self.wait_for_ready_state_complete()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.06)
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            element.clear()
            if not new_value.endswith('\n'):
                element.send_keys(new_value)
            else:
                new_value = new_value[:-1]
                element.send_keys(new_value)
                element.send_keys(Keys.RETURN)
                if Settings.WAIT_FOR_RSC_ON_PAGE_LOADS:
                    self.wait_for_ready_state_complete()
        if (retry and element.get_attribute('value') != new_value and (
                not new_value.endswith('\n'))):
            logging.debug('update_text_value is falling back to jQuery!')
            selector = self.jq_format(selector)
            self.set_value(selector, new_value, by=by)

    def update_text(self, selector, new_value, by=By.CSS_SELECTOR,
                    timeout=Settings.SMALL_TIMEOUT, retry=False):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.update_text_value(selector, new_value, by=by,
                               timeout=timeout, retry=retry)

    def js_update_date(self,selector, new_value):
        if selector.startswith('#'):
            selector=selector[1:]
            js = "document.getElementById('%s').value='%s'" % (selector, new_value)
        elif "name" in selector:
            selector = selector.split("'")[1]
            js = "document.getElementsByName('%s')[0].value='%s'" % (selector, new_value)
        self.execute_script(js)

    def is_element_present(self, selector, by=By.CSS_SELECTOR):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.is_element_present(self.driver, selector, by)

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.is_element_visible(self.driver, selector, by)

    def is_element_selected(self, selector, by=By.CSS_SELECTOR):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.is_element_selected(self.driver, selector, by)

    def is_link_text_visible(self, link_text):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        return PageActions.is_element_visible(self.driver, link_text,
                                               by=By.LINK_TEXT)

    def is_partial_link_text_visible(self, partial_link_text):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        return PageActions.is_element_visible(self.driver, partial_link_text,
                                               by=By.PARTIAL_LINK_TEXT)

    def is_text_visible(self, text, selector, by=By.CSS_SELECTOR):
        self.wait_for_ready_state_complete()
        time.sleep(0.01)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.is_text_visible(self.driver, text, selector, by)

    def find_visible_elements(self, selector, by=By.CSS_SELECTOR):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.find_visible_elements(self.driver, selector, by)

    def find_btn_and_click(self,selector,text):
        resultTag = False
        try:
            btnlist = self.find_visible_elements(selector)
            for btn in btnlist:
                if btn.text == text:
                    btn.click()
                    resultTag = True
                    break
        finally:
            return resultTag

    def execute_script(self, script):
        return self.driver.execute_script(script)

    def execute_async_script(self, script, timeout=Settings.EXTREME_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.EXTREME_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.driver.set_script_timeout(timeout)
        return self.driver.execute_async_script(script)

    def set_window_size(self, width, height):
        self.driver.set_window_size(width, height)

    def maximize_window(self):
        pass
        self.driver.maximize_window()

    def activate_jquery(self):
        try:
            self.execute_script("jQuery('html')")
            return
        except Exception:
            pass
        self.execute_script(
            '''var script = document.createElement("script"); '''
            '''script.src = "http://code.jquery.com/jquery-3.1.0.min.js"; '''
            '''document.getElementsByTagName("head")[0]'''
            '''.appendChild(script);''')
        for x in range(30):
            try:
                self.execute_script("jQuery('html')")
                return
            except Exception:
                time.sleep(0.1)
        raise Exception("Exception: WebDriver could not activate jQuery!")

    def highlight(self, selector, by=By.CSS_SELECTOR,
                  loops=Settings.HIGHLIGHTS, scroll=True):
        element = self.find_element(
            selector, by=by, timeout=Settings.SMALL_TIMEOUT)
        if scroll:
            self._slow_scroll_to_element(element)
        try:
            selector = self.convert_to_css_selector(selector, by=by)
        except Exception:
            return

        last_syllable = selector.split(' ')[-1]
        if ':' not in last_syllable:
            selector += ':first'

        o_bs = ''
        style = element.get_attribute('style')
        if style:
            if 'box-shadow: ' in style:
                box_start = style.find('box-shadow: ')
                box_end = style.find(';', box_start) + 1
                original_box_shadow = style[box_start:box_end]
                o_bs = original_box_shadow

        script = """jQuery('%s').css('box-shadow',
            '0px 0px 6px 6px rgba(128, 128, 128, 0.5)');""" % selector
        try:
            self.execute_script(script)
        except Exception:
            self.activate_jquery()
            self.execute_script(script)
        if self.highlights:
            loops = self.highlights
        loops = int(loops)
        for n in range(loops):
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(255, 0, 0, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(128, 0, 128, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(0, 0, 255, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(0, 255, 0, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(128, 128, 0, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)
            script = """jQuery('%s').css('box-shadow',
                '0px 0px 6px 6px rgba(128, 0, 128, 1)');""" % selector
            self.execute_script(script)
            time.sleep(0.02)

        script = """jQuery('%s').css('box-shadow', '%s');""" % (selector, o_bs)
        self.execute_script(script)
        time.sleep(0.065)

    def scroll_to(self, selector, by=By.CSS_SELECTOR,
                  timeout=Settings.SMALL_TIMEOUT):
        ''' Fast scroll to destination '''
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        try:
            self._scroll_to_element(element)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.wait_for_element_visible(
                selector, by=by, timeout=timeout)
            self._scroll_to_element(element)

    def slow_scroll_to(self, selector, by=By.CSS_SELECTOR,
                       timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        self._slow_scroll_to_element(element)

    def scroll_click(self, selector, by=By.CSS_SELECTOR):
        self.scroll_to(selector, by=by)
        self.click(selector, by=by)

    def click_xpath(self, xpath):
        self.click(xpath, by=By.XPATH)

    def jquery_click(self, selector, by=By.CSS_SELECTOR):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        selector = self.convert_to_css_selector(selector, by=by)
        self.wait_for_element_present(
            selector, by=by, timeout=Settings.SMALL_TIMEOUT)

        # Only get the first match
        last_syllable = selector.split(' ')[-1]
        if ':' not in last_syllable:
            selector += ':first'

        click_script = """jQuery('%s')[0].click()""" % selector
        try:
            self.execute_script(click_script)
        except Exception:
            self.activate_jquery()
            self.execute_script(click_script)

    def jq_format(self, code):
        return PageUtils.jq_format(code)

    def get_domain_url(self, url):
        return PageUtils.get_domain_url(url)

    def download_file(self, file_url, destination_folder=None):
        if not destination_folder:
            destination_folder = Constants.Files.DOWNLOADS_FOLDER
        PageUtils._download_file_to(file_url, destination_folder)

    def save_file_as(self, file_url, new_file_name, destination_folder=None):
        if not destination_folder:
            destination_folder = Constants.Files.DOWNLOADS_FOLDER
        PageUtils._download_file_to(
            file_url, destination_folder, new_file_name)

    def convert_XpathToCss(self, xpath):
        return XpathToCss.convert_XpathToCss(xpath)

    def convert_to_css_selector(self, selector, by):
        if by == By.CSS_SELECTOR:
            return selector
        elif by == By.ID:
            return '#%s' % selector
        elif by == By.CLASS_NAME:
            return '.%s' % selector
        elif by == By.NAME:
            return '[name="%s"]' % selector
        elif by == By.TAG_NAME:
            return selector
        elif by == By.XPATH:
            return self.convert_XpathToCss(selector)
        elif by == By.LINK_TEXT:
            return 'a:contains("%s")' % selector
        elif by == By.PARTIAL_LINK_TEXT:
            return 'a:contains("%s")' % selector
        else:
            raise Exception(
                "Exception: Could not convert [%s](by=%s) to CSS_SELECTOR!" % (
                    selector, by))

    def set_value(self, selector, new_value, by=By.CSS_SELECTOR,
                  timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        selector = self.convert_to_css_selector(selector, by=by)
        self.scroll_to(selector, by=by, timeout=timeout)
        value = json.dumps(new_value)

        last_syllable = selector.split(' ')[-1]
        if ':' not in last_syllable:
            selector += ':first'

        set_value_script = """jQuery('%s').val(%s)""" % (selector, value)
        try:
            self.execute_script(set_value_script)
        except Exception:
            self.activate_jquery()  # It's a good thing we can define it here
            self.execute_script(set_value_script)

    def jquery_update_text_value(self, selector, new_value, by=By.CSS_SELECTOR,
                                 timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        element = self.wait_for_element_visible(
            selector, by=by, timeout=timeout)
        self.scroll_to(selector, by=by)
        selector = self.convert_to_css_selector(selector, by=by)

        last_syllable = selector.split(' ')[-1]
        if ':' not in last_syllable:
            selector += ':first'

        update_text_script = """jQuery('%s').val('%s')""" % (
            selector, self.jq_format(new_value))
        try:
            self.execute_script(update_text_script)
        except Exception:
            self.activate_jquery()  # It's a good thing we can define it here
            self.execute_script(update_text_script)
        if new_value.endswith('\n'):
            element.send_keys('\n')

    def jquery_update_text(self, selector, new_value, by=By.CSS_SELECTOR,
                           timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.jquery_update_text_value(
            selector, new_value, by=by, timeout=timeout)

    def hover_on_element(self, selector, by=By.CSS_SELECTOR):
        self.wait_for_element_visible(
            selector, by=by, timeout=Settings.SMALL_TIMEOUT)
        self.scroll_to(selector, by=by)
        time.sleep(0.05)
        return PageActions.hover_on_element(self.driver, selector)

    def hover_and_click(self, hover_selector, click_selector,
                        hover_by=By.CSS_SELECTOR, click_by=By.CSS_SELECTOR,
                        timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(hover_selector):
            hover_by = By.XPATH
        if PageUtils.is_xpath_selector(click_selector):
            click_by = By.XPATH
        self.wait_for_element_visible(
            hover_selector, by=hover_by, timeout=timeout)
        self.scroll_to(hover_selector, by=hover_by)
        pre_action_url = self.driver.current_url
        element = PageActions.hover_and_click(
                self.driver, hover_selector, click_selector,
                hover_by, click_by, timeout)
        return element

    def pick_select_option_by_text(self, dropdown_selector, option,
                                   dropdown_by=By.CSS_SELECTOR,
                                   timeout=Settings.SMALL_TIMEOUT):
        """ Picks an HTML <select> option by option text. """
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self._pick_select_option(dropdown_selector, option,
                                 dropdown_by=dropdown_by, option_by="text",
                                 timeout=timeout)

    def pick_select_option_by_index(self, dropdown_selector, option,
                                    dropdown_by=By.CSS_SELECTOR,
                                    timeout=Settings.SMALL_TIMEOUT):
        """ Picks an HTML <select> option by option index. """
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self._pick_select_option(dropdown_selector, option,
                                 dropdown_by=dropdown_by, option_by="index",
                                 timeout=timeout)

    def pick_select_option_by_value(self, dropdown_selector, option,
                                    dropdown_by=By.CSS_SELECTOR,
                                    timeout=Settings.SMALL_TIMEOUT):
        """ Picks an HTML <select> option by option value. """
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self._pick_select_option(dropdown_selector, option,
                                 dropdown_by=dropdown_by, option_by="value",
                                 timeout=timeout)

    ############

    def wait_for_element_present(self, selector, by=By.CSS_SELECTOR,
                                 timeout=Settings.LARGE_TIMEOUT):
        """ Waits for an element to appear in the HTML of a page.
            The element does not need be visible (it may be hidden). """
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.wait_for_element_present(
            self.driver, selector, by, timeout)

    def assert_element_present(self, selector, by=By.CSS_SELECTOR,
                               timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_element_present(selector, by=by, timeout=timeout)
        return True

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR,
                                 timeout=Settings.LARGE_TIMEOUT):
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.wait_for_element_visible(
            self.driver, selector, by, timeout)

    def wait_for_element(self, selector, by=By.CSS_SELECTOR,
                         timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_element_visible(selector, by=by, timeout=timeout)

    def find_element(self, selector, by=By.CSS_SELECTOR,
                     timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_element_visible(selector, by=by, timeout=timeout)

    def assert_element(self, selector, by=By.CSS_SELECTOR,
                       timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_element_visible(selector, by=by, timeout=timeout)
        return True

    def wait_for_text_visible(self, text, selector, by=By.CSS_SELECTOR,
                              timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.wait_for_text_visible(
            self.driver, text, selector, by, timeout)

    def wait_for_text(self, text, selector, by=By.CSS_SELECTOR,
                      timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_text_visible(
            text, selector, by=by, timeout=timeout)

    def find_text(self, text, selector, by=By.CSS_SELECTOR,
                  timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_text_visible(
            text, selector, by=by, timeout=timeout)

    def assert_text(self, text, selector, by=By.CSS_SELECTOR,
                    timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_text_visible(text, selector, by=by, timeout=timeout)
        return True

    def wait_for_link_text_visible(self, link_text,
                                   timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_element_visible(
            link_text, by=By.LINK_TEXT, timeout=timeout)

    def wait_for_link_text(self, link_text, timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_link_text_visible(link_text, timeout=timeout)

    def find_link_text(self, link_text, timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_link_text_visible(link_text, timeout=timeout)

    def assert_link_text(self, link_text, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_link_text_visible(link_text, timeout=timeout)
        return True

    def wait_for_partial_link_text(self, partial_link_text,
                                   timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_element_visible(
            partial_link_text, by=By.PARTIAL_LINK_TEXT, timeout=timeout)

    def find_partial_link_text(self, partial_link_text,
                               timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return self.wait_for_partial_link_text(
            partial_link_text, timeout=timeout)

    def assert_partial_link_text(self, partial_link_text,
                                 timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_partial_link_text(partial_link_text, timeout=timeout)
        return True

    def wait_for_element_absent(self, selector, by=By.CSS_SELECTOR,
                                timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.wait_for_element_absent(
            self.driver, selector, by, timeout)

    def assert_element_absent(self, selector, by=By.CSS_SELECTOR,
                              timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_element_absent(selector, by=by, timeout=timeout)
        return True

    def wait_for_element_not_visible(self, selector, by=By.CSS_SELECTOR,
                                     timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if PageUtils.is_xpath_selector(selector):
            by = By.XPATH
        return PageActions.wait_for_element_not_visible(
            self.driver, selector, by, timeout)

    def assert_element_not_visible(self, selector, by=By.CSS_SELECTOR,
                                   timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        self.wait_for_element_not_visible(selector, by=by, timeout=timeout)
        return True

    def wait_for_ready_state_complete(self, timeout=Settings.EXTREME_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.EXTREME_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        is_ready = PageActions.wait_for_ready_state_complete(self.driver,
                                                              timeout)
        self.wait_for_angularjs()
        return is_ready

    def wait_for_angularjs(self, timeout=Settings.EXTREME_TIMEOUT, **kwargs):
        if self.timeout_multiplier and timeout == Settings.EXTREME_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        if not Settings.WAIT_FOR_ANGULARJS:
            return

        NG_WRAPPER = '%(prefix)s' \
                     'var $elm=document.querySelector(' \
                     '\'[data-ng-app],[ng-app],.ng-scope\')||document;' \
                     'if(window.angular && angular.getTestability){' \
                     'angular.getTestability($elm).whenStable(%(handler)s)' \
                     '}else{' \
                     'var $inj;try{$inj=angular.element($elm).injector()||' \
                     'angular.injector([\'ng\'])}catch(ex){' \
                     '$inj=angular.injector([\'ng\'])};$inj.get=$inj.get||' \
                     '$inj;$inj.get(\'$browser\').' \
                     'notifyWhenNoOutstandingRequests(%(handler)s)}' \
                     '%(suffix)s'
        def_pre = 'var cb=arguments[arguments.length-1];if(window.angular){'
        prefix = kwargs.pop('prefix', def_pre)
        handler = kwargs.pop('handler', 'function(){cb(true)}')
        suffix = kwargs.pop('suffix', '}else{cb(false)}')
        script = NG_WRAPPER % {'prefix': prefix,
                               'handler': handler,
                               'suffix': suffix}
        try:
            self.execute_async_script(script, timeout=timeout)
        except:
            pass

    def wait_for_and_accept_alert(self, timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return PageActions.wait_for_and_accept_alert(self.driver, timeout)

    def wait_for_and_dismiss_alert(self, timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return PageActions.wait_for_and_dismiss_alert(self.driver, timeout)

    def wait_for_and_switch_to_alert(self, timeout=Settings.LARGE_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.LARGE_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        return PageActions.wait_for_and_switch_to_alert(self.driver, timeout)

    def switch_to_frame(self, frame, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        PageActions.switch_to_frame(self.driver, frame, timeout)

    def switch_to_parent_frame(self, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        PageActions.switch_to_parent_frame(self.driver, timeout)

    def switch_to_window(self, window, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        PageActions.switch_to_window(self.driver, window, timeout)

    def current_window_handle(self, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        PageActions.switch_to_window(self.driver, timeout)

    def window_handles(self, timeout=Settings.SMALL_TIMEOUT):
        if self.timeout_multiplier and timeout == Settings.SMALL_TIMEOUT:
            timeout = self._get_new_timeout(timeout)
        PageActions.window_handles(self.driver, timeout)

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def save_screenshot(self, name, folder=None):
        return PageActions.save_screenshot(self.driver, name, folder)

    def _get_new_timeout(self, timeout):
        """ When using --timeout_multiplier=#.# """
        try:
            timeout_multiplier = float(self.timeout_multiplier)
            if timeout_multiplier <= 0.5:
                timeout_multiplier = 0.5
            timeout = int(math.ceil(timeout_multiplier * timeout))
            return timeout
        except:
            return timeout

    ############

    def _get_exception_message(self):
        if sys.version.startswith('3') and hasattr(self, '_outcome'):
            exception_info = self._outcome.errors
            if exception_info:
                try:
                    exc_message = exception_info[0][1][1]
                except:
                    exc_message = "(Unknown Exception)"
            else:
                exc_message = "(Unknown Exception)"
        else:
            exception_info = sys.exc_info()[1]
            if hasattr(exception_info, 'msg'):
                exc_message = exception_info.msg
            elif hasattr(exception_info, 'message'):
                exc_message = exception_info.message
            else:
                exc_message = '(Unknown Exception)'
        return exc_message

    def _package_check(self):
        current_url = self.driver.current_url
        message = self._get_exception_message()
        self.page_check_failures.append(
                "CHECK #%s: (%s)\n %s" % (
                    self.page_check_count, current_url, message))

    def check_assert_element(self, selector, by=By.CSS_SELECTOR,
                             timeout=Settings.MINI_TIMEOUT):
        self.page_check_count += 1
        try:
            self.wait_for_element_visible(selector, by=by, timeout=timeout)
            return True
        except Exception:
            self._package_check()
            return False

    def check_assert_text(self, text, selector, by=By.CSS_SELECTOR,
                          timeout=Settings.MINI_TIMEOUT):
        self.page_check_count += 1
        try:
            self.wait_for_text_visible(text, selector, by=by, timeout=timeout)
            return True
        except Exception:
            self._package_check()
            return False

    def process_checks(self, print_only=False):
        if self.page_check_failures:
            exception_output = ''
            exception_output += "\n*** FAILED CHECKS FOR: %s\n" % self.id()
            all_failing_checks = self.page_check_failures
            self.page_check_failures = []
            for tb in all_failing_checks:
                exception_output += "%s\n" % tb
            if print_only:
                print(exception_output)
            else:
                raise Exception(exception_output)

    def _pick_select_option(self, dropdown_selector, option,
                            dropdown_by=By.CSS_SELECTOR, option_by="text",
                            timeout=Settings.SMALL_TIMEOUT):
        element = self.find_element(
            dropdown_selector, by=dropdown_by, timeout=timeout)
        pre_action_url = self.driver.current_url
        try:
            if option_by == "index":
                Select(element).select_by_index(option)
            elif option_by == "value":
                Select(element).select_by_value(option)
            else:
                Select(element).select_by_visible_text(option)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete()
            time.sleep(0.05)
            element = self.find_element(
                dropdown_selector, by=dropdown_by, timeout=timeout)
            if option_by == "index":
                Select(element).select_by_index(option)
            elif option_by == "value":
                Select(element).select_by_value(option)
            else:
                Select(element).select_by_visible_text(option)
        if Settings.WAIT_FOR_RSC_ON_CLICKS:
            self.wait_for_ready_state_complete()

    def _scroll_to_element(self, element):
        element_location = element.location['y']
        element_location = element_location - 130
        if element_location < 0:
            element_location = 0
        scroll_script = "window.scrollTo(0, %s);" % element_location
        self.execute_script(scroll_script)

    def _slow_scroll_to_element(self, element):
        scroll_position = self.execute_script("return window.scrollY;")
        element_location = element.location['y']
        element_location = element_location - 130
        if element_location < 0:
            element_location = 0
        distance = element_location - scroll_position
        if distance != 0:
            total_steps = int(abs(distance) / 50.0) + 2.0
            step_value = float(distance) / total_steps
            new_position = scroll_position
            for y in range(int(total_steps)):
                time.sleep(0.0114)
                new_position += step_value
                scroll_script = "window.scrollTo(0, %s);" % new_position
                self.execute_script(scroll_script)
        time.sleep(0.01)
        scroll_script = "window.scrollTo(0, %s);" % element_location
        self.execute_script(scroll_script)
        time.sleep(0.01)
        if distance > 430 or distance < -300:
            time.sleep(0.162)

